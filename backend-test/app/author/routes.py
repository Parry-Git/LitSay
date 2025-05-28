from flask import jsonify, request, current_app, g
from . import author_bp
from app.db import query_db
from app.utils.decorators import login_required

@author_bp.route('/<int:author_id>', methods=['GET'])
@login_required
def get_author_detail(author_id):
    """获取作者详情及其文章列表"""
    user_id = g.current_user['user_id']
    
    try:
        # 获取作者基本信息
        author = query_db("""
            SELECT author_id, author_name, author_email
            FROM author
            WHERE author_id = %s AND user_id = %s
        """, (author_id, user_id), one=True)
        
        if not author:
            return jsonify({"error": "未找到", "message": "作者不存在或无权访问"}), 404
        
        # 获取作者所属机构
        institutions = query_db("""
            SELECT i.institution_id, i.institution_name, i.institution_location
            FROM institution i
            JOIN author_institution ai ON i.institution_id = ai.institution_id
            WHERE ai.author_id = %s AND i.user_id = %s
        """, (author_id, user_id))
        
        # 获取作者参与的文章及其角色
        documents = query_db("""
            SELECT d.document_id, d.title, d.publication_date, da.sequence,
                  dir.directory_name, dir.directory_id
            FROM document d
            JOIN document_author da ON d.document_id = da.document_id
            JOIN directory dir ON d.directory_id = dir.directory_id
            WHERE da.author_id = %s AND d.user_id = %s
            ORDER BY d.publication_date DESC
        """, (author_id, user_id))
        
        # 构建响应数据
        result = {
            "id": author['author_id'],
            "name": author['author_name'],
            "email": author['author_email'],
            "institutions": institutions,
            "documents": documents,
            "documentCount": len(documents)
        }
        
        return jsonify({
            "code": 0,
            "message": "获取成功",
            "data": result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取作者详情失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"获取作者详情失败: {str(e)}"}), 500
