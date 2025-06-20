from flask import request, jsonify, current_app, g
from . import user_bp
from app.db import query_db, get_db
from app.utils.decorators import login_required, admin_required

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

@user_bp.route('/all', methods=['GET'])
@login_required
@admin_required  # 新增权限装饰器确保仅管理员可访问
def get_all_users():
    """获取所有用户列表，仅限管理员使用"""
    try:
        users = query_db("""
            SELECT user_id, user_name as username, 
                   CASE WHEN role = 1 THEN 'admin' ELSE 'user' END as role
            FROM user
            ORDER BY user_id
        """)
        
        return jsonify({
            "code": 0, 
            "message": "获取用户列表成功", 
            "data": users
        })
    except Exception as e:
        current_app.logger.error(f"获取用户列表失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500, 
            "message": f"获取用户列表失败: {str(e)}"
        }), 500

@user_bp.route('/<int:user_id>/role', methods=['PUT'])
@login_required
@admin_required
def update_user_role(user_id):
    """更新用户角色，仅限管理员使用"""
    data = request.get_json()
    if not data or 'role' not in data:
        return jsonify({"code": 400, "message": "缺少角色参数"}), 400
    
    new_role = data['role']
    # 将角色名称转换为数字表示
    role_value = 1 if new_role == 'admin' else 0
    
    # 检查用户是否存在
    user = query_db("SELECT * FROM user WHERE user_id = %s", (user_id,), one=True)
    if not user:
        return jsonify({"code": 404, "message": f"用户ID {user_id} 不存在"}), 404

    # 防止自降级：当前用户不能更改自己的角色
    if user_id == g.current_user['user_id']:
        return jsonify({"code": 403, "message": "不能更改自己的角色"}), 403
    
    try:
        # 更新用户角色
        query_db("UPDATE user SET role = %s WHERE user_id = %s", 
                (role_value, user_id), commit=True)
        
        return jsonify({
            "code": 0, 
            "message": f"用户角色已更新为 {new_role}"
        })
    except Exception as e:
        current_app.logger.error(f"更新用户角色失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500, 
            "message": f"更新用户角色失败: {str(e)}"
        }), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """删除用户及其所有相关数据，仅限管理员使用"""
    # 检查用户是否存在
    user = query_db("SELECT * FROM user WHERE user_id = %s", (user_id,), one=True)
    if not user:
        return jsonify({"code": 404, "message": f"用户ID {user_id} 不存在"}), 404
    
    # 检查要删除的用户是否为管理员
    if user['role'] == 1:
        return jsonify({"code": 403, "message": "不能删除管理员账户"}), 403
    
    # 防止自删除：当前用户不能删除自己
    if user_id == g.current_user['user_id']:
        return jsonify({"code": 403, "message": "不能删除自己的账户"}), 403
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 开始事务，保证删除操作的原子性
        cursor.execute("START TRANSACTION")
        
        # 1. 删除用户的文档关联
        cursor.execute("""
            DELETE FROM document_author WHERE document_id IN
            (SELECT document_id FROM document WHERE user_id = %s)
        """, (user_id,))
        
        cursor.execute("""
            DELETE FROM document_keyword WHERE document_id IN
            (SELECT document_id FROM document WHERE user_id = %s)
        """, (user_id,))
        
        # 2. 删除用户的文档
        cursor.execute("DELETE FROM document WHERE user_id = %s", (user_id,))
        
        # 3. 删除用户的目录
        cursor.execute("DELETE FROM directory_closure WHERE ancestor_id IN (SELECT directory_id FROM directory WHERE user_id = %s)", (user_id,))
        cursor.execute("DELETE FROM directory_closure WHERE descendant_id IN (SELECT directory_id FROM directory WHERE user_id = %s)", (user_id,))
        cursor.execute("DELETE FROM directory WHERE user_id = %s", (user_id,))
        
        # 4. 删除用户的关键词
        cursor.execute("DELETE FROM keyword WHERE user_id = %s", (user_id,))
        
        # 5. 最后删除用户账户
        cursor.execute("DELETE FROM user WHERE user_id = %s", (user_id,))
        
        # 提交事务
        cursor.execute("COMMIT")
        
        conn.commit()
        
        return jsonify({
            "code": 0,
            "message": f"用户ID {user_id} 及其所有数据已成功删除"
        })
    except Exception as e:
        # 发生异常，回滚事务
        if conn:
            conn.rollback()
        current_app.logger.error(f"删除用户失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500,
            "message": f"删除用户失败: {str(e)}"
        }), 500
