# 占个位，后续可能会写

from flask import jsonify, current_app, g
from . import user_bp
from app.db import query_db
from app.utils.decorators import login_required

@user_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    """获取用户统计数据"""
    user_id = g.current_user['user_id']
    
    try:
        # 查询用户的总文档数
        total_documents = query_db("""
            SELECT COUNT(*) as count FROM document
            WHERE user_id = %s
        """, (user_id,), one=True)
        
        # 查询用户的总文件夹数
        total_folders = query_db("""
            SELECT COUNT(*) as count FROM directory
            WHERE user_id = %s
        """, (user_id,), one=True)
        
        # 查询最近查看的文档数
        recently_viewed = query_db("""
            SELECT COUNT(*) as count FROM document
            WHERE user_id = %s AND create_time > DATE_SUB(NOW(), INTERVAL 7 DAY)
        """, (user_id,), one=True)
        
        # 组装统计数据
        stats = {
            "totalDocuments": total_documents['count'] if total_documents else 0,
            "totalFolders": total_folders['count'] if total_folders else 0,
            "recentlyViewed": recently_viewed['count'] if recently_viewed else 0
        }
        
        return jsonify({
            "code": 0,
            "message": "获取成功",
            "data": stats
        })
        
    except Exception as e:
        current_app.logger.error(f"获取用户统计数据失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"获取用户统计数据失败: {str(e)}"}), 500
