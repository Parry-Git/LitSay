from flask import jsonify, request, current_app, g
from . import institution_bp
from app.db import query_db
from app.utils.decorators import login_required

@institution_bp.route('/<int:institution_id>', methods=['GET'])
@login_required
def get_institution_detail(institution_id):
    """获取机构详情及其作者列表"""
    user_id = g.current_user['user_id']
    
    try:
        # 获取机构基本信息
        institution = query_db("""
            SELECT institution_id, institution_name, institution_location
            FROM institution
            WHERE institution_id = %s AND user_id = %s
        """, (institution_id, user_id), one=True)
        
        if not institution:
            return jsonify({"error": "未找到", "message": "机构不存在或无权访问"}), 404
        
        # 获取机构下的作者
        authors = query_db("""
            SELECT a.author_id, a.author_name, a.author_email
            FROM author a
            JOIN author_institution ai ON a.author_id = ai.author_id
            WHERE ai.institution_id = %s AND a.user_id = %s
            ORDER BY a.author_name
        """, (institution_id, user_id))
        
        # 构建响应数据
        result = {
            "id": institution['institution_id'],
            "name": institution['institution_name'],
            "location": institution['institution_location'],
            "authors": authors,
            "authorCount": len(authors)
        }
        
        return jsonify({
            "code": 0,
            "message": "获取成功",
            "data": result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取机构详情失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"获取机构详情失败: {str(e)}"}), 500
