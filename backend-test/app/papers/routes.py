from flask import request, jsonify, current_app, g
from . import papers_bp
from app.db import query_db
from app.utils.decorators import token_required

@papers_bp.route('', methods=['POST'])
@token_required
def add_paper():
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'message': 'Title is required'}), 400

    title = data.get('title')
    authors = data.get('authors', '')
    abstract = data.get('abstract', '')
    keywords = data.get('keywords', '')
    publication_year = data.get('publication_year')
    user_id = g.current_user_id # From @token_required

    try:
        paper_id = query_db(
            "INSERT INTO papers (title, authors, abstract, keywords, publication_year, user_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (title, authors, abstract, keywords, publication_year, user_id),
            commit=True
        )
        return jsonify({'message': 'Paper added successfully', 'paper_id': paper_id}), 201
    except Exception as e:
        current_app.logger.error(f"Failed to add paper: {e}")
        return jsonify({'message': 'Failed to add paper'}), 500

@papers_bp.route('', methods=['GET'])
@token_required # Or make it public if desired
def get_papers():
    # Basic pagination (optional)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    offset = (page - 1) * per_page

    # Search term (simple keyword search)
    search_term = request.args.get('q', '')

    query = "SELECT p.id, p.title, p.authors, p.publication_year, u.username as owner FROM papers p JOIN users u ON p.user_id = u.id"
    params = []

    if search_term:
        # Basic search across title, authors, keywords, abstract
        # Note: For OceanBase (MySQL mode), LIKE is case-insensitive by default for non-binary strings.
        # For full-text search, consider OceanBase's full-text capabilities if available or use dedicated search engines.
        query += " WHERE (p.title LIKE %s OR p.authors LIKE %s OR p.keywords LIKE %s OR p.abstract LIKE %s)"
        like_term = f"%{search_term}%"
        params.extend([like_term] * 4)
    
    # Add user filter if only want papers by the current user
    # query += " AND p.user_id = %s"
    # params.append(g.current_user_id)

    query += " ORDER BY p.upload_date DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    try:
        papers = query_db(query, tuple(params))
        # You might also want to get total count for pagination
        count_query = "SELECT COUNT(*) as total FROM papers" # Add WHERE clause if search is applied
        # total_count = query_db(count_query, tuple(params_for_count_only), one=True)['total']
        return jsonify(papers), 200
    except Exception as e:
        current_app.logger.error(f"Failed to get papers: {e}")
        return jsonify({'message': 'Failed to retrieve papers'}), 500

@papers_bp.route('/<int:paper_id>', methods=['GET'])
@token_required # Or public
def get_paper_detail(paper_id):
    try:
        paper = query_db("SELECT * FROM papers WHERE id = %s", (paper_id,), one=True)
        if paper:
            # Check if paper belongs to user or if user is admin, if implementing ownership
            # if paper['user_id'] != g.current_user_id:
            #     return jsonify({'message': 'Access denied'}), 403
            return jsonify(paper), 200
        return jsonify({'message': 'Paper not found'}), 404
    except Exception as e:
        current_app.logger.error(f"Failed to get paper detail: {e}")
        return jsonify({'message': 'Failed to retrieve paper detail'}), 500