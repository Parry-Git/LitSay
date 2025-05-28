from flask import request, jsonify, current_app, g
from . import folders_bp
from app.db import query_db, get_db, close_db
from app.utils.decorators import login_required
import os

@folders_bp.route('/tree', methods=['GET'])
@login_required
def get_folder_tree():
    """获取文件夹树结构"""
    user_id = g.current_user['user_id']
    try:
        # 使用闭包表查询所有文件夹结构
        folders = query_db("""
            SELECT d.directory_id as id, d.directory_name as label, d.parent_id,
                   c.ancestor_id, c.depth
            FROM directory d
            JOIN directory_closure c ON d.directory_id = c.descendant_id
            WHERE d.user_id = %s
            ORDER BY c.depth, d.directory_name
        """, (user_id,))

        if not folders:
            # 如果没有文件夹，创建默认根文件夹，这里暂时写的是根目录，后续可以考虑换个别的名字
            root_dir_id = query_db("""
                INSERT INTO directory (user_id, parent_id, directory_name)
                VALUES (%s, NULL, %s)
            """, (user_id, "根目录"), commit=True)
            
            # 为根目录添加自引用闭包关系
            query_db("""
                INSERT INTO directory_closure (ancestor_id, descendant_id, depth, user_id)
                VALUES (%s, %s, %s, %s)
            """, (root_dir_id, root_dir_id, 0, user_id), commit=True)
            
            # 添加"我的文献库"文件夹
            my_lib_id = query_db("""
                INSERT INTO directory (user_id, parent_id, directory_name)
                VALUES (%s, %s, %s)
            """, (user_id, root_dir_id, "我的文献库"), commit=True)
            
            # 添加闭包关系
            query_db("""
                INSERT INTO directory_closure (ancestor_id, descendant_id, depth, user_id)
                VALUES (%s, %s, %s, %s), (%s, %s, %s, %s)
            """, (my_lib_id, my_lib_id, 0, user_id, root_dir_id, my_lib_id, 1, user_id), commit=True)
            
            # 重新查询文件夹结构
            folders = query_db("""
                SELECT d.directory_id as id, d.directory_name as label, d.parent_id,
                       c.ancestor_id, c.depth
                FROM directory d
                JOIN directory_closure c ON d.directory_id = c.descendant_id
                WHERE d.user_id = %s
                ORDER BY c.depth, d.directory_name
            """, (user_id,))
        
        # 构建树结构
        folder_dict = {}
        root_folders = []
        
        # 首先创建所有文件夹节点
        for folder in folders:
            if folder['id'] not in folder_dict:
                folder_dict[folder['id']] = {
                    'id': folder['id'],
                    'label': folder['label'],
                    'children': []
                }
        
        # 然后建立父子关系
        for folder in folders:
            # 仅处理深度为1的关系（直接父子关系）
            if folder['depth'] == 1:
                parent_id = folder['ancestor_id']
                child_id = folder['id']
                
                if parent_id in folder_dict and child_id in folder_dict and parent_id != child_id:
                    folder_dict[parent_id]['children'].append(folder_dict[child_id])
        
        # 找出所有根文件夹
        for folder in folders:
            if folder['parent_id'] is None and folder['id'] in folder_dict:
                root_folders.append(folder_dict[folder['id']])
        
        return jsonify({
            "code": 0,
            "message": "获取成功",
            "data": root_folders
        })
        
    except Exception as e:
        current_app.logger.error(f"获取文件夹树结构失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"获取文件夹树结构失败: {str(e)}"}), 500

@folders_bp.route('/<int:folder_id>', methods=['GET'])
@login_required
def get_folder_contents(folder_id):
    """获取文件夹内容"""
    user_id = g.current_user['user_id']
    try:
        # 检查文件夹存在并属于当前用户
        folder = query_db("""
            SELECT directory_id, directory_name, parent_id
            FROM directory
            WHERE directory_id = %s AND user_id = %s
        """, (folder_id, user_id), one=True)
        
        if not folder:
            return jsonify({"error": "未找到", "message": "文件夹不存在或无权访问"}), 404
        
        # 获取子文件夹
        subfolders = query_db("""
            SELECT d.directory_id as id, d.directory_name as name, 
                   'folder' as type, d.create_time as createTime
            FROM directory d
            JOIN directory_closure c ON d.directory_id = c.descendant_id
            WHERE c.ancestor_id = %s AND c.depth = 1 AND d.user_id = %s
        """, (folder_id, user_id))
        
        # 获取文件夹中的文档
        documents = query_db("""
            SELECT document_id as id, title as name, 
                   'document' as type, create_time as createTime
            FROM document
            WHERE directory_id = %s AND user_id = %s
            ORDER BY create_time DESC
        """, (folder_id, user_id))
        
        # 结合子文件夹和文档
        items = subfolders + documents
        
        # 获取父文件夹路径
        path = ""
        if folder['parent_id']:
            parent_path = query_db("""
                WITH RECURSIVE folder_path AS (
                    SELECT d.directory_id, d.directory_name, d.parent_id, 
                           CAST(d.directory_name AS CHAR(1000)) AS path
                    FROM directory d
                    WHERE d.directory_id = %s
                    
                    UNION ALL
                    
                    SELECT d.directory_id, d.directory_name, d.parent_id,
                           CONCAT(d.directory_name, '/', p.path)
                    FROM directory d
                    JOIN folder_path p ON d.directory_id = p.parent_id
                    WHERE d.parent_id IS NOT NULL
                )
                SELECT path FROM folder_path
                WHERE parent_id IS NULL
            """, (folder['parent_id'],), one=True)
            
            if parent_path:
                path = parent_path['path']
        
        # 构造当前文件夹对象
        current_folder = {
            "id": folder['directory_id'],
            "name": folder['directory_name'],
            "path": path.rstrip('/'),
            "parentId": folder['parent_id']
        }
        
        return jsonify({
            "code": 0,
            "message": "获取成功",
            "data": {
                "currentFolder": current_folder,
                "items": items
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取文件夹内容失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"获取文件夹内容失败: {str(e)}"}), 500

@folders_bp.route('/create', methods=['POST'])
@login_required
def create_folder():
    """创建文件夹"""
    user_id = g.current_user['user_id']
    data = request.json
    
    if not data:
        return jsonify({"error": "参数错误", "message": "请求缺少必要参数"}), 400
    
    parent_id = data.get('parentId')
    name = data.get('name')
    
    if not name or not parent_id:
        return jsonify({"error": "参数错误", "message": "文件夹名称和父文件夹ID不能为空"}), 400
    
    try:
        # 检查父文件夹是否存在并属于当前用户
        parent_folder = query_db("""
            SELECT directory_id FROM directory
            WHERE directory_id = %s AND user_id = %s
        """, (parent_id, user_id), one=True)
        
        if not parent_folder:
            return jsonify({"error": "未找到", "message": "父文件夹不存在或无权访问"}), 404
        
        # 检查同级目录下是否有同名文件夹
        existing_folder = query_db("""
            SELECT directory_id FROM directory
            WHERE parent_id = %s AND directory_name = %s AND user_id = %s
        """, (parent_id, name, user_id), one=True)
        
        if existing_folder:
            return jsonify({"error": "操作冲突", "message": "同级目录下已存在同名文件夹"}), 409
        
        # 创建新文件夹
        new_folder_id = query_db("""
            INSERT INTO directory (user_id, parent_id, directory_name)
            VALUES (%s, %s, %s)
        """, (user_id, parent_id, name), commit=True)
        
        # 添加闭包表关系
        # 1. 首先插入自身关系(深度为0)
        query_db("""
            INSERT INTO directory_closure (ancestor_id, descendant_id, depth, user_id)
            VALUES (%s, %s, %s, %s)
        """, (new_folder_id, new_folder_id, 0, user_id), commit=True)
        
        # 2. 然后插入从所有祖先到自身的关系
        query_db("""
            INSERT INTO directory_closure (ancestor_id, descendant_id, depth, user_id)
            SELECT c.ancestor_id, %s, c.depth + 1, %s
            FROM directory_closure c
            WHERE c.descendant_id = %s
        """, (new_folder_id, user_id, parent_id), commit=True)
        
        return jsonify({
            "code": 0,
            "message": "创建成功",
            "data": {
                "id": new_folder_id,
                "name": name,
                "type": "folder",
                "createTime": None,  # API返回时会自动转换为当前时间
                "parentId": parent_id
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"创建文件夹失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"创建文件夹失败: {str(e)}"}), 500

@folders_bp.route('/rename', methods=['PUT'])
@login_required
def rename_folder():
    """重命名文件夹"""
    user_id = g.current_user['user_id']
    data = request.json
    
    if not data:
        return jsonify({"error": "参数错误", "message": "请求缺少必要参数"}), 400
    
    folder_id = data.get('folderId')
    new_name = data.get('newName')
    
    if not folder_id or not new_name:
        return jsonify({"error": "参数错误", "message": "文件夹ID和新名称不能为空"}), 400
    
    try:
        # 检查文件夹是否存在并属于当前用户
        folder = query_db("""
            SELECT directory_id, parent_id FROM directory
            WHERE directory_id = %s AND user_id = %s
        """, (folder_id, user_id), one=True)
        
        if not folder:
            return jsonify({"error": "未找到", "message": "文件夹不存在或无权访问"}), 404
        
        # 检查同级目录下是否有同名文件夹
        existing_folder = query_db("""
            SELECT directory_id FROM directory
            WHERE parent_id = %s AND directory_name = %s AND user_id = %s AND directory_id != %s
        """, (folder['parent_id'], new_name, user_id, folder_id), one=True)
        
        if existing_folder:
            return jsonify({"error": "操作冲突", "message": "同级目录下已存在同名文件夹"}), 409
        
        # 更新文件夹名称
        query_db("""
            UPDATE directory
            SET directory_name = %s
            WHERE directory_id = %s AND user_id = %s
        """, (new_name, folder_id, user_id), commit=True)
        
        return jsonify({
            "code": 0,
            "message": "重命名成功",
            "data": {
                "id": folder_id,
                "name": new_name
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"重命名文件夹失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"重命名文件夹失败: {str(e)}"}), 500

@folders_bp.route('/<int:folder_id>', methods=['DELETE'])
@login_required
def delete_folder(folder_id):
    """删除文件夹"""
    user_id = g.current_user['user_id']
    
    try:
        # 检查文件夹是否存在并属于当前用户
        folder = query_db("""
            SELECT directory_id FROM directory
            WHERE directory_id = %s AND user_id = %s
        """, (folder_id, user_id), one=True)
        
        if not folder:
            return jsonify({"error": "未找到", "message": "文件夹不存在或无权访问"}), 404
        
        # 获取所有子文件夹ID
        subfolder_ids = query_db("""
            SELECT descendant_id FROM directory_closure
            WHERE ancestor_id = %s AND depth > 0 AND user_id = %s
        """, (folder_id, user_id))
        
        subfolder_ids = [item['descendant_id'] for item in subfolder_ids]
        subfolder_ids.append(folder_id)  # 也包括当前文件夹
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # 开始事务
            conn.start_transaction()
            
            # 1. 删除这些文件夹中的所有文档
            for subfolder_id in subfolder_ids:
                # 查找该文件夹中的文档
                cursor.execute("""
                    SELECT document_id, local_url FROM document
                    WHERE directory_id = %s AND user_id = %s
                """, (subfolder_id, user_id))
                
                documents = cursor.fetchall()
                
                # 删除每个文档的物理文件
                for doc in documents:
                    try:
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc['local_url'])
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        current_app.logger.error(f"删除文件失败: {e}")
                
                # 删除数据库中的文档记录(会通过外键级联删除相关的author, keyword关系)
                cursor.execute("""
                    DELETE FROM document
                    WHERE directory_id = %s AND user_id = %s
                """, (subfolder_id, user_id))
            
            # 2. 删除文件夹闭包关系 - 修改这里，使用SQL的IN操作符处理列表
            placeholders = ', '.join(['%s'] * len(subfolder_ids))
            
            # 为每个参数添加user_id
            params = subfolder_ids + [user_id]
            cursor.execute(f"""
                DELETE FROM directory_closure
                WHERE descendant_id IN ({placeholders}) AND user_id = %s
            """, params)
            
            # 同样修改这个查询
            params = subfolder_ids + [user_id]
            cursor.execute(f"""
                DELETE FROM directory_closure
                WHERE ancestor_id IN ({placeholders}) AND user_id = %s
            """, params)
            
            # 3. 最后删除文件夹 - 同样修改
            params = subfolder_ids + [user_id]
            cursor.execute(f"""
                DELETE FROM directory
                WHERE directory_id IN ({placeholders}) AND user_id = %s
            """, params)
            
            # 提交事务
            conn.commit()
            
        except Exception as e:
            # 回滚事务
            conn.rollback()
            current_app.logger.error(f"删除文件夹事务失败: {e}")
            raise e
        finally:
            close_db()
        
        return jsonify({
            "code": 0,
            "message": "删除成功"
        })
        
    except Exception as e:
        current_app.logger.error(f"删除文件夹失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"删除文件夹失败: {str(e)}"}), 500
