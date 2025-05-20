import os
from flask import request, jsonify, current_app, g
from werkzeug.utils import secure_filename

from . import papers_bp
from app.db import query_db
from app.utils.decorators import login_required


ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@papers_bp.route('/upload', methods=['POST'])
@login_required
def upload_paper():
    if 'file' not in request.files:
        return jsonify({"error": "Validation Error", "message": "No file part in the request."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Validation Error", "message": "No file selected for uploading."}), 400
    
    title = request.form.get('title')
    directory_id_str = request.form.get('directory_id')
    doi = request.form.get('doi', None)
    container_id_str = request.form.get('container_id', None)
    publication_date = request.form.get('publication_date', None) # Expecting YYYY-MM-DD HH:MM:SS or YYYY-MM-DD

    if not title:
        return jsonify({"error": "Validation Error", "message": "Title is required."}), 400
    if not directory_id_str:
        return jsonify({"error": "Validation Error", "message": "Directory ID is required."}), 400

    try:
        directory_id = int(directory_id_str)
    except ValueError:
        return jsonify({"error": "Validation Error", "message": "Invalid Directory ID format."}), 400

    container_id = None
    if container_id_str:
        try:
            container_id = int(container_id_str)
        except ValueError:
            return jsonify({"error": "Validation Error", "message": "Invalid Container ID format."}), 400


    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        user_id = g.current_user['user_id']

        # Create user-specific upload folder if it doesn't exist
        user_upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
        os.makedirs(user_upload_folder, exist_ok=True)
        
        file_path = os.path.join(user_upload_folder, filename)
        
        # Prevent overwriting, or handle versioning if needed
        if os.path.exists(file_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(user_upload_folder, f"{base}_{counter}{ext}")):
                counter += 1
            filename = f"{base}_{counter}{ext}"
            file_path = os.path.join(user_upload_folder, filename)

        try:
            file.save(file_path)
            # Relative path to store in DB
            local_url = os.path.relpath(file_path, current_app.config['UPLOAD_FOLDER'])

            # dir_check = query_db("SELECT 1 FROM directory WHERE directory_id = %s AND user_id = %s", (directory_id, user_id), one=True)
            # if not dir_check:
            #     return jsonify({"error": "Validation Error", "message": "Invalid or unauthorized directory_id."}), 400
            # Similarly for container_id if provided

            sql = """
            INSERT INTO document (directory_id, container_id, user_id, title, doi, local_url, publication_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            args = (directory_id, container_id, user_id, title, doi, local_url, publication_date)
            document_id = query_db(sql, args, commit=True)
            return jsonify({
                "message": "File uploaded and paper metadata saved successfully.",
                "document_id": document_id,
                "filename": filename,
                "local_url": local_url
            }), 201

        except Exception as e:
            current_app.logger.error(f"File upload or DB insert error: {e}")
            # Clean up uploaded file if DB insert fails
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": "Server Error", "message": f"Could not process file upload: {str(e)}"}), 500
    else:
        return jsonify({"error": "Validation Error", "message": "File type not allowed."}), 400

@papers_bp.route('/search', methods=['GET'])
@login_required
def search_papers():
    query_param = request.args.get('q', '')
    user_id = g.current_user['user_id'] # Search only user's papers

    if not query_param:
        return jsonify({"error": "Validation Error", "message": "Search query 'q' is required."}), 400

    search_term = f"%{query_param}%"
    
    # Simple search by title for now. Can be extended to search DOI, authors, keywords etc.
    sql = """
    SELECT document_id, title, doi, local_url, publication_date, create_time 
    FROM document 
    WHERE user_id = %s AND title LIKE %s
    ORDER BY create_time DESC
    """
    try:
        papers = query_db(sql, (user_id, search_term))
        return jsonify(papers), 200
    except Exception as e:
        current_app.logger.error(f"Search error: {e}")
        return jsonify({"error": "Server Error", "message": "Could not perform search."}), 500

@papers_bp.route('/', methods=['GET'])
@login_required
def list_user_papers():
    user_id = g.current_user['user_id']
    try:
        # might add pagination here for large datasets
        papers = query_db("SELECT document_id, title, doi, local_url, publication_date, create_time FROM document WHERE user_id = %s ORDER BY create_time DESC", (user_id,))
        return jsonify(papers), 200
    except Exception as e:
        current_app.logger.error(f"Error listing papers: {e}")
        return jsonify({"error": "Server Error", "message": "Could not retrieve papers."}), 500

@papers_bp.route('/<int:document_id>', methods=['GET'])
@login_required
def get_paper_details(document_id):
    user_id = g.current_user['user_id']
    try:
        paper = query_db("""
            SELECT d.document_id, d.title, d.doi, d.local_url, d.publication_date, d.create_time,
                   dir.directory_name, c.container_name, c.type as container_type
            FROM document d
            JOIN directory dir ON d.directory_id = dir.directory_id
            LEFT JOIN container c ON d.container_id = c.container_id
            WHERE d.document_id = %s AND d.user_id = %s
        """, (document_id, user_id), one=True)
        
        if not paper:
            return jsonify({"error": "Not Found", "message": "Paper not found or access denied."}), 404
        
        # Optionally, fetch authors and keywords
        authors = query_db("""
            SELECT a.author_name, da.sequence 
            FROM author a
            JOIN document_author da ON a.author_id = da.author_id
            WHERE da.document_id = %s ORDER BY da.sequence
        """, (document_id,))
        
        keywords = query_db("""
            SELECT k.keyword_name
            FROM keyword k
            JOIN document_keyword dk ON k.keyword_id = dk.keyword_id
            WHERE dk.document_id = %s
        """, (document_id,))

        paper['authors'] = authors
        paper['keywords'] = keywords
        
        return jsonify(paper), 200
    except Exception as e:
        current_app.logger.error(f"Error getting paper details: {e}")
        return jsonify({"error": "Server Error", "message": "Could not retrieve paper details."}), 500
