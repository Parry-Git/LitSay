from flask import jsonify, request, current_app, g
from . import container_bp
from app.db import query_db
from app.utils.decorators import login_required

@container_bp.route('/<int:container_id>', methods=['GET'])
@login_required
def get_container_detail(container_id):
    """获取容器（期刊或会议）详情及相关文献"""
    user_id = g.current_user['user_id']
    
    try:
        # 获取容器基本信息
        container = query_db("""
            SELECT container_id, container_name, type, 
                   journal_issue, conference_time, conference_location
            FROM container
            WHERE container_id = %s AND user_id = %s
        """, (container_id, user_id), one=True)
        
        if not container:
            return jsonify({"error": "未找到", "message": "期刊/会议不存在或无权访问"}), 404
        
        container_name = container['container_name']
        # 获取容器关联的所有文献，注意此处通过container_name而不是container_id
        # 以便支持同名容器的情况
        documents = query_db("""
            SELECT d.document_id, d.title, d.doi, d.publication_date, c.container_name, 
            c.journal_issue, c.conference_time, c.conference_location
            FROM document d
            JOIN container c ON d.container_id = c.container_id
            WHERE c.container_name = %s AND d.user_id = %s
            ORDER BY d.publication_date DESC
        """, (container_name, user_id))
        
        # 构建响应数据
        result = {
            "id": container['container_id'],
            "name": container['container_name'],
            "type": container['type'],
            "journalIssue": container['journal_issue'],
            "conferenceTime": container['conference_time'],
            "conferenceLocation": container['conference_location'],
            "documents": documents,
            "documentCount": len(documents)
        }
        
        return jsonify({
            "code": 0,
            "message": "获取成功",
            "data": result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取容器详情失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"获取容器详情失败: {str(e)}"}), 500
