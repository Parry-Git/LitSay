import os
from flask import request, jsonify, current_app, g
from werkzeug.utils import secure_filename

from . import documents_bp
from app.db import query_db, get_db, close_db
from app.utils.decorators import login_required

@documents_bp.route('/<int:document_id>', methods=['GET'])
@login_required
def get_document_details(document_id):
    """获取文档详情"""
    user_id = g.current_user['user_id']
    
    try:
        document = query_db("""
            SELECT d.document_id, d.title, d.doi, d.local_url, 
                   d.publication_date as publishDate, d.create_time as uploadTime,
                   dir.directory_name as folderName, dir.directory_id as folderId,
                   d.stars, d.note, d.container_id
            FROM document d
            JOIN directory dir ON d.directory_id = dir.directory_id
            WHERE d.document_id = %s AND d.user_id = %s
        """, (document_id, user_id), one=True)
        
        if not document:
            return jsonify({"error": "未找到", "message": "文档不存在或无权访问"}), 404
        
        authors_data = query_db("""
            SELECT a.author_id, a.author_name, da.sequence, 
                   i.institution_name, i.institution_location, a.author_email
            FROM author a
            JOIN document_author da ON a.author_id = da.author_id
            LEFT JOIN author_institution ai ON a.author_id = ai.author_id
            LEFT JOIN institution i ON ai.institution_id = i.institution_id
            WHERE da.document_id = %s
            ORDER BY CASE da.sequence
                WHEN 'first' THEN 1
                WHEN 'corresponding' THEN 2
                WHEN 'additional' THEN 3
                WHEN 'other' THEN 4
                ELSE 5
            END
        """, (document_id,))
        
        keywords = query_db("""
            SELECT k.keyword_name
            FROM keyword k
            JOIN document_keyword dk ON k.keyword_id = dk.keyword_id
            WHERE dk.document_id = %s
        """, (document_id,))
        
        result = {
            "id": document['document_id'],
            "title": document['title'],
            "authors": [],
            "author_ids": [],  # 明确添加author_ids数组
            "sequence": [],
            "institutions": [],
            "institution_location": [],
            "email": [],
            "doi": document['doi'],
            "publishDate": document['publishDate'].strftime('%Y-%m-%d') if document['publishDate'] else None,
            "uploadTime": document['uploadTime'].strftime('%Y-%m-%d %H:%M:%S') if document['uploadTime'] else None,
            "journal": None,
            "conference": None,
            "keywords": [keyword['keyword_name'] for keyword in keywords],
            "folderId": document['folderId'],
            "folderName": document['folderName'],
            "note": document['note'],
            "stars": document['stars'],
            "local_url": document['local_url'],
            "container_id": document['container_id']  # 明确返回container_id
        }
        
        # 处理作者信息 - 直接使用字符串sequence，并添加机构和地址
        for author in authors_data:
            result['authors'].append(author['author_name'])
            result['author_ids'].append(author['author_id'])  # 存储作者ID
            result['sequence'].append(author['sequence'] if author['sequence'] else 'other')
            result['institutions'].append(author['institution_name'] if author['institution_name'] else '')
            result['institution_location'].append(author['institution_location'] if author['institution_location'] else '')
            result['email'].append(author['author_email'] if author['author_email'] else '')
        
        # 获取期刊或会议信息
        container_info = query_db("""
            SELECT c.container_name, c.type
            FROM document d
            JOIN container c ON d.container_id = c.container_id
            WHERE d.document_id = %s
        """, (document_id,), one=True)
        
        if container_info:
            if container_info['type'] == 'journal':
                result['journal'] = container_info['container_name']
            else:
                result['conference'] = container_info['container_name']
        
        return jsonify({
            "code": 0,
            "message": "获取成功",
            "data": result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取文档详情失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"获取文档详情失败: {str(e)}"}), 500

@documents_bp.route('/<int:document_id>/metadata', methods=['PUT'])
@login_required
def update_document_metadata(document_id):
    """更新文档元数据"""
    user_id = g.current_user['user_id']
    data = request.json
    
    if not data:
        return jsonify({"error": "参数错误", "message": "请求缺少必要参数"}), 400
    
    try:
        # 检查文档是否存在并属于当前用户
        document = query_db("""
            SELECT document_id FROM document
            WHERE document_id = %s AND user_id = %s
        """, (document_id, user_id), one=True)
        
        if not document:
            return jsonify({"error": "未找到", "message": "文档不存在或无权访问"}), 404
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # 开始事务
            conn.start_transaction()
            
            # 1. 更新文档基本信息
            update_fields = []
            update_values = []
            
            if 'title' in data:
                update_fields.append("title = %s")
                update_values.append(data['title'])
            
            if 'doi' in data:
                update_fields.append("doi = %s")
                update_values.append(data['doi'])
            
            if 'publishDate' in data:
                update_fields.append("publication_date = %s")
                update_values.append(data['publishDate'])
            
            if 'note' in data:
                update_fields.append("note = %s")
                update_values.append(data['note'])
            
            if 'stars' in data:
                update_fields.append("stars = %s")
                update_values.append(data['stars'])
            
            if update_fields:
                update_query = f"""
                    UPDATE document
                    SET {', '.join(update_fields)}
                    WHERE document_id = %s AND user_id = %s
                """
                update_values.extend([document_id, user_id])
                cursor.execute(update_query, update_values)
            
            # 2. 处理作者信息
            if 'authors' in data and isinstance(data['authors'], list):
                # 删除现有作者关联
                cursor.execute("""
                    DELETE FROM document_author
                    WHERE document_id = %s
                """, (document_id,))
                
                # 添加新作者关联
                for i, author_name in enumerate(data['authors']):
                    if not author_name:
                        continue
                    
                    # 获取作者相关信息
                    sequence = data.get('sequence', [])[i] if i < len(data.get('sequence', [])) else "additional"
                    institution = data.get('institutions', [])[i] if i < len(data.get('institutions', [])) else ""
                    location = data.get('institution_location', [])[i] if i < len(data.get('institution_location', [])) else ""
                    email = data.get('email', [])[i] if i < len(data.get('email', [])) else ""
                    
                    # 确保sequence为有效值
                    if sequence not in ["first", "corresponding", "additional", "other"]:
                        sequence = "additional"
                    
                    # 查找或创建作者
                    cursor.execute("""
                        SELECT author_id FROM author
                        WHERE author_name = %s AND user_id = %s
                    """, (author_name, user_id))
                    
                    author_result = cursor.fetchone()
                    if author_result:
                        author_id = author_result['author_id']
                        # 更新作者邮箱信息
                        cursor.execute("""
                            UPDATE author SET author_email = %s
                            WHERE author_id = %s
                        """, (email, author_id))
                    else:
                        cursor.execute("""
                            INSERT INTO author (author_name, user_id, author_email)
                            VALUES (%s, %s, %s)
                        """, (author_name, user_id, email))
                        author_id = cursor.lastrowid
                    
                    # 关联作者与文档
                    cursor.execute("""
                        INSERT INTO document_author (document_id, author_id, sequence)
                        VALUES (%s, %s, %s)
                    """, (document_id, author_id, sequence))
                    
                    # 处理机构信息
                    if institution:
                        # 查找或创建机构
                        cursor.execute("""
                            SELECT institution_id FROM institution
                            WHERE institution_name = %s AND user_id = %s
                        """, (institution, user_id))
                        
                        institution_result = cursor.fetchone()
                        if institution_result:
                            institution_id = institution_result['institution_id']
                            # 更新机构地址
                            cursor.execute("""
                                UPDATE institution SET institution_location = %s
                                WHERE institution_id = %s
                            """, (location, institution_id))
                        else:
                            cursor.execute("""
                                INSERT INTO institution (institution_name, institution_location, user_id)
                                VALUES (%s, %s, %s)
                            """, (institution, location, user_id))
                            institution_id = cursor.lastrowid
                        
                        # 删除旧的作者-机构关联
                        cursor.execute("""
                            DELETE FROM author_institution
                            WHERE author_id = %s
                        """, (author_id,))
                        
                        # 创建新的作者-机构关联
                        cursor.execute("""
                            INSERT INTO author_institution (author_id, institution_id)
                            VALUES (%s, %s)
                        """, (author_id, institution_id))
            
            # 3. 处理关键词信息
            if 'keywords' in data and isinstance(data['keywords'], list):
                # 删除现有关键词关联
                cursor.execute("""
                    DELETE FROM document_keyword
                    WHERE document_id = %s
                """, (document_id,))
                
                # 添加新关键词关联
                for keyword in data['keywords']:
                    if not keyword:
                        continue
                    
                    # 查找或创建关键词
                    cursor.execute("""
                        SELECT keyword_id FROM keyword
                        WHERE keyword_name = %s AND user_id = %s
                    """, (keyword, user_id))
                    
                    keyword_result = cursor.fetchone()
                    if keyword_result:
                        keyword_id = keyword_result['keyword_id']
                    else:
                        cursor.execute("""
                            INSERT INTO keyword (keyword_name, user_id)
                            VALUES (%s, %s)
                        """, (keyword, user_id))
                        keyword_id = cursor.lastrowid
                    
                    # 关联关键词与文档
                    cursor.execute("""
                        INSERT INTO document_keyword (document_id, keyword_id)
                        VALUES (%s, %s)
                    """, (document_id, keyword_id))
            
            # 4. 处理期刊/会议信息
            journal = data.get('journal')
            conference = data.get('conference')
            
            if journal or conference:
                # 检查文档是否已关联容器
                cursor.execute("""
                    SELECT container_id FROM document
                    WHERE document_id = %s
                """, (document_id,))
                
                doc_container = cursor.fetchone()
                container_id = doc_container['container_id'] if doc_container else None
                
                # 确定容器类型和名称
                container_type = 'journal' if journal else 'conference'
                container_name = journal or conference
                
                if container_id:
                    # 更新现有容器
                    cursor.execute("""
                        UPDATE container
                        SET type = %s, container_name = %s
                        WHERE container_id = %s AND user_id = %s
                    """, (container_type, container_name, container_id, user_id))
                else:
                    # 创建新容器，确保添加必要字段以符合约束条件
                    if container_type == 'journal':
                        cursor.execute("""
                            INSERT INTO container (user_id, type, container_name, journal_issue)
                            VALUES (%s, %s, %s, %s)
                        """, (user_id, container_type, container_name, "Vol. 1"))
                    else:  # conference
                        publish_date = data.get('publishDate') or "2023-01-01"
                        cursor.execute("""
                            INSERT INTO container (user_id, type, container_name, conference_time)
                            VALUES (%s, %s, %s, %s)
                        """, (user_id, container_type, container_name, publish_date))
                    
                    container_id = cursor.lastrowid
                    
                    # 关联文档与容器
                    cursor.execute("""
                        UPDATE document
                        SET container_id = %s
                        WHERE document_id = %s
                    """, (container_id, document_id))
            
            # 提交事务
            conn.commit()
            
            return jsonify({
                "code": 0,
                "message": "更新成功",
                "data": {
                    "id": document_id
                }
            })
            
        except Exception as e:
            # 回滚事务
            conn.rollback()
            current_app.logger.error(f"更新文档元数据事务失败: {e}")
            raise e
        finally:
            close_db()
        
    except Exception as e:
        current_app.logger.error(f"更新文档元数据失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"更新文档元数据失败: {str(e)}"}), 500

@documents_bp.route('/<int:document_id>', methods=['DELETE'])
@login_required
def delete_document(document_id):
    """删除文档"""
    user_id = g.current_user['user_id']
    
    try:
        # 检查文档是否存在并属于当前用户
        document = query_db("""
            SELECT document_id, local_url FROM document
            WHERE document_id = %s AND user_id = %s
        """, (document_id, user_id), one=True)
        
        if not document:
            return jsonify({"error": "未找到", "message": "文档不存在或无权访问"}), 404
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            # 开始事务
            conn.start_transaction()
            
            # # 1. 删除文档的物理文件
            # if document['local_url']:
            #     file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document['local_url'])
            #     if os.path.exists(file_path):
            #         os.remove(file_path)
            
            # 2. 删除文档记录(会通过外键级联删除相关的author, keyword关系)
            cursor.execute("""
                DELETE FROM document
                WHERE document_id = %s AND user_id = %s
            """, (document_id, user_id))
            
            # 提交事务
            conn.commit()
            
            return jsonify({
                "code": 0,
                "message": "删除成功"
            })
            
        except Exception as e:
            # 回滚事务
            conn.rollback()
            current_app.logger.error(f"删除文档事务失败: {e}")
            raise e
        finally:
            close_db()
        
    except Exception as e:
        current_app.logger.error(f"删除文档失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"删除文档失败: {str(e)}"}), 500
