from flask import request, jsonify, current_app, g, send_file
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime, timezone

from . import documents_bp
from app.db import query_db
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
            LEFT JOIN institution i ON i.institution_id = da.institution_id
            WHERE da.document_id = %s
            ORDER BY CASE da.sequence
                WHEN 'first' THEN 1
                WHEN 'corresponding' THEN 2
                WHEN 'additional' THEN 3
                WHEN 'other' THEN 4
                ELSE 5
            END
        """, (document_id,))
        print(f"获取文档ID {document_id} 的作者信息: {authors_data}")
        
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
            "journal_issue": None,  # 期刊期号
            "conference_time": None,  # 会议时间
            "conference": None,
            "conference_location": None,  # 会议地点
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
            SELECT c.container_name, c.type, c.journal_issue, c.conference_time, c.conference_location
            FROM document d
            JOIN container c ON d.container_id = c.container_id
            WHERE d.document_id = %s
        """, (document_id,), one=True)
        
        if container_info:
            if container_info['type'] == 'journal':
                result['journal'] = container_info['container_name']
                result['journal_issue'] = container_info['journal_issue']
            else:
                result['conference'] = container_info['container_name']
                result['conference_time'] = container_info['conference_time']
                result['conference_location'] = container_info['conference_location']
        
        return jsonify({
            "code": 0,
            "message": "获取成功",
            "data": result
        })
        
    except Exception as e:
        current_app.logger.error(f"获取文档详情失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"获取文档详情失败: {str(e)}"}), 500

@documents_bp.route('/<int:document_id>', methods=['DELETE'])
@login_required
def delete_document(document_id):
    user_id = g.current_user['user_id']
    
    try:
        # 验证文档归属
        document = query_db(
            "SELECT * FROM document WHERE document_id = %s AND user_id = %s", 
            (document_id, user_id), 
            one=True
        )
        
        if not document:
            return jsonify({"error": "NotFound", "message": "文档不存在或无权访问"}), 404
            
        # 开始删除操作
        # 1. 获取文档相关的作者ID，以便后续检查是否需要删除作者
        authors_query = """
            SELECT author_id FROM document_author 
            WHERE document_id = %s
        """
        authors = query_db(authors_query, (document_id,))
        author_ids = [a['author_id'] for a in authors]
        
        # 1.1 获取文档相关的关键词ID，以便后续检查是否需要删除
        keywords_query = """
            SELECT keyword_id FROM document_keyword 
            WHERE document_id = %s
        """
        keywords = query_db(keywords_query, (document_id,))
        keyword_ids = [k['keyword_id'] for k in keywords]
        
        print(f"删除文档关联的关键词IDs: {keyword_ids}")
        
        # 2. 删除文档-关键词关系
        print(f"删除文档-关键词关系: document_id = {document_id}")
        query_db(
            "DELETE FROM document_keyword WHERE document_id = %s",
            (document_id,),
            commit=True
        )
        
        # 3. 删除文档-作者关系
        print(f"删除文档-作者关系: document_id = {document_id}")
        query_db(
            "DELETE FROM document_author WHERE document_id = %s",
            (document_id,),
            commit=True
        )
        
        # 4. 检查是否存在容器关联
        container_id = document.get('container_id')
        if container_id:
            # 检查容器是否还被其他文档引用
            container_check = query_db(
                "SELECT COUNT(*) as doc_count FROM document WHERE container_id = %s AND document_id != %s",
                (container_id, document_id),
                one=True
            )
            
            # 如果没有其他文档引用此容器，删除容器
            if container_check and container_check['doc_count'] == 0:
                print(f"删除容器: container_id = {container_id}")
                query_db("DELETE FROM container WHERE container_id = %s", (container_id,), commit=True)
        
        # 5. 删除文档本身
        print(f"删除文档: document_id = {document_id}")
        query_db(
            "DELETE FROM document WHERE document_id = %s",
            (document_id,),
            commit=True
        )
        
        # 6. 检查作者是否需要删除
        for author_id in author_ids:
            clean_unused_author(author_id, user_id)
        
        # 6.1 检查关键词是否需要删除
        for keyword_id in keyword_ids:
            clean_unused_keyword(keyword_id, user_id)
        
                
        return jsonify({
            "code": 0,
            "message": "文档删除成功"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"删除文档失败: {e}")
        return jsonify({"error": "ServerError", "message": f"删除文档失败: {str(e)}"}), 500

@documents_bp.route('/<int:document_id>/metadata', methods=['PUT'])
@login_required
def update_document_metadata(document_id):
    user_id = g.current_user['user_id']
    data = request.json
    format_string = '%a, %d %b %Y %H:%M:%S %Z'
    print("更新文档元数据:\n", data)
    
    if not data:
        return jsonify({"error": "BadRequest", "message": "未提供更新数据"}), 400
    
    try:
        # 验证文档归属
        document = query_db(
            "SELECT * FROM document WHERE document_id = %s AND user_id = %s", 
            (document_id, user_id), 
            one=True
        )
        
        if not document:
            return jsonify({"error": "NotFound", "message": "文档不存在或无权访问"}), 404
            
        # 更新文档基本信息
        update_fields = []
        update_values = []
        
        # 可更新字段列表
        allowed_fields = ['title', 'doi', 'publication_date', 'stars', 'note', 'local_url']
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                update_values.append(data[field])
        
        # 处理容器(期刊/会议)信息
        old_container_id = document.get('container_id')
        new_container_id = None
        
        if 'journal' in data or 'conference' in data:
            # 确定容器类型
            container_type = 'journal' if data.get('journal') else 'conference'
            container_name = data.get('journal') or data.get('conference')
            # 收集容器特定字段
            journal_issue = data.get('journal_issue')
            # conference_time = datetime.strptime(data.get('conference_time'), format_string)
            conference_time = data.get('conference_time')
            conference_location = data.get('conference_location')
            
            if container_name:
                # 检查是否存在相同类型、名称的容器
                existing_container = query_db(
                    "SELECT container_id FROM container WHERE container_name = %s AND type = %s AND user_id = %s AND journal_issue = %s AND conference_time = %s AND conference_location = %s",
                    (container_name, container_type, user_id, journal_issue, conference_time, conference_location),
                    one=True
                )
                
                if existing_container:
                    # 使用现有容器
                    new_container_id = existing_container['container_id']
                    print(f"使用现有容器: container_id = {new_container_id}")
                else:
                    # 创建新容器
                    print(f"创建新容器: name = {container_name}, type = {container_type}")
                    
                    new_container_id = query_db(
                        """INSERT INTO container 
                           (container_name, type, user_id, journal_issue, conference_time, conference_location) 
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (container_name, container_type, user_id, journal_issue, conference_time, conference_location),
                        commit=True
                    )
                
                # 添加容器ID到更新字段
                update_fields.append("container_id = %s")
                update_values.append(new_container_id)
            else:
                # 移除容器关联
                update_fields.append("container_id = NULL")
            
        # 更新文档基本信息
        if update_fields:
            sql = f"UPDATE document SET {', '.join(update_fields)} WHERE document_id = %s AND user_id = %s"
            update_values.extend([document_id, user_id])
            
            print(f"更新文档基本信息: {sql}")
            print(f"更新值: {update_values}")
            
            query_db(sql, update_values, commit=True)
        
        # 处理旧容器
        if old_container_id and (old_container_id != new_container_id):
            # 检查旧容器是否还被其他文档引用
            container_check = query_db(
                "SELECT COUNT(*) as doc_count FROM document WHERE container_id = %s AND document_id != %s",
                (old_container_id, document_id),
                one=True
            )
            
            # 如果没有其他文档引用此容器，删除容器
            if container_check and container_check['doc_count'] == 0:
                print(f"删除旧容器: container_id = {old_container_id}")
                query_db("DELETE FROM container WHERE container_id = %s", (old_container_id,), commit=True)
                
        # 处理作者更新
        if 'authors' in data:
            # 获取当前文档的作者
            current_authors = query_db(
                "SELECT author_id FROM document_author WHERE document_id = %s",
                (document_id,)
            )
            current_author_ids = {a['author_id'] for a in current_authors}
            
            # 处理新作者
            new_authors = data.get('authors', [])
            new_author_ids = set()
            
            for i, author_name in enumerate(new_authors):
                if not author_name:
                    continue
                
                # 准备作者相关字段
                sequence = data.get('sequence', [])[i] if i < len(data.get('sequence', [])) else "additional"
                institution_name = data.get('institutions', [])[i] if i < len(data.get('institutions', [])) else None
                location = data.get('institution_location', [])[i] if i < len(data.get('institution_location', [])) else None
                email = data.get('email', [])[i] if i < len(data.get('email', [])) else None
                
                # 查找或创建作者
                author = query_db(
                    "SELECT author_id FROM author WHERE author_name = %s AND user_id = %s",
                    (author_name, user_id),
                    one=True
                )
                
                if author:
                    author_id = author['author_id']
                    print(f"找到现有作者: author_id = {author_id}, name = {author_name}")
                else:
                    author_id = query_db(
                        "INSERT INTO author (author_name, user_id) VALUES (%s, %s)",
                        (author_name, user_id),
                        commit=True
                    )
                    print(f"创建新作者: author_id = {author_id}, name = {author_name}")
                
                new_author_ids.add(author_id)
                
                # 查找或创建机构（如果有）
                institution_id = None
                if institution_name:
                    institution = query_db(
                        "SELECT institution_id, institution_location FROM institution WHERE institution_name = %s AND user_id = %s",
                        (institution_name, user_id),
                        one=True
                    )
                    
                    if institution:
                        institution_id = institution['institution_id']
                        print(f"找到现有机构: institution_id = {institution_id}, name = {institution_name}")
                        # 如果元数据中提供了新的地址信息，则更新机构地址
                        # location comes from data.get('institution_location', [])[i]
                        if location is not None: # Check if location is explicitly provided in input
                            if location != institution.get('institution_location'):
                                institution_update_sql = "UPDATE institution SET institution_location = %s WHERE institution_id = %s AND user_id = %s"
                                print(f"SQL: 更新机构地址 - {institution_update_sql}")
                                print(f"SQL参数: ({location}, {institution_id}, {user_id})")
                                query_db(
                                    institution_update_sql,
                                    (location, institution_id, user_id),
                                    commit=True
                                )
                                print(f"机构地址更新成功: name='{institution_name}', new_location='{location}'")
                            else:
                                print(f"机构地址未改变: name='{institution_name}', location='{location}'")
                        else:
                            print(f"未提供机构地址更新信息 for name='{institution_name}'")
                    else:
                        institution_id = query_db(
                            "INSERT INTO institution (institution_name, institution_location, user_id) VALUES (%s, %s, %s)",
                            (institution_name, location, user_id),
                            commit=True
                        )
                        print(f"创建新机构: institution_id = {institution_id}, name = {institution_name}, location = {location}")
                    
                    # 检查作者-机构关联是否已存在
                    author_institution = query_db(
                        "SELECT 1 FROM author_institution WHERE author_id = %s AND institution_id = %s",
                        (author_id, institution_id),
                        one=True
                    )
                    
                    if not author_institution:
                        # 创建作者-机构关联
                        print(f"创建作者-机构关联: author_id = {author_id}, institution_id = {institution_id}")
                        query_db(
                            "INSERT INTO author_institution (author_id, institution_id) VALUES (%s, %s)",
                            (author_id, institution_id),
                            commit=True
                        )
                
                # 检查作者-文档关联是否已存在
                doc_author = query_db(
                    "SELECT 1 FROM document_author WHERE document_id = %s AND author_id = %s",
                    (document_id, author_id),
                    one=True
                )
                
                if doc_author:
                    # 更新作者-文档关联
                    print(f"更新作者-文档关联: document_id = {document_id}, author_id = {author_id}")
                    query_db(
                        """UPDATE document_author 
                           SET sequence = %s, institution_id = %s 
                           WHERE document_id = %s AND author_id = %s""",
                        (sequence, institution_id, document_id, author_id),
                        commit=True
                    )
                else:
                    # 创建作者-文档关联
                    print(f"创建作者-文档关联: document_id = {document_id}, author_id = {author_id}")
                    query_db(
                        """INSERT INTO document_author 
                           (document_id, author_id, sequence, institution_id) 
                           VALUES (%s, %s, %s, %s)""",
                        (document_id, author_id, sequence, institution_id),
                        commit=True
                    )
                    
            # 找出删除的作者
            removed_author_ids = current_author_ids - new_author_ids
            
            for author_id in removed_author_ids:
                # 删除作者-文档关联
                print(f"删除作者-文档关联: document_id = {document_id}, author_id = {author_id}")
                query_db(
                    "DELETE FROM document_author WHERE document_id = %s AND author_id = %s",
                    (document_id, author_id),
                    commit=True
                )
                
                # 检查是否需要删除作者
                clean_unused_author(author_id, user_id)
        
        # 处理关键词更新
        if 'keywords' in data:
            # 获取当前文档的关键词
            current_keywords = query_db(
                """SELECT k.keyword_id, k.keyword_name 
                   FROM keyword k
                   JOIN document_keyword dk ON k.keyword_id = dk.keyword_id
                   WHERE dk.document_id = %s AND k.user_id = %s""",
                (document_id, user_id)
            )
            current_keyword_map = {k['keyword_name']: k['keyword_id'] for k in current_keywords}
            
            # 删除旧的文档-关键词关联
            query_db(
                "DELETE FROM document_keyword WHERE document_id = %s",
                (document_id,),
                commit=True
            )
            
            # 添加新的关键词和关联
            for keyword in data.get('keywords', []):
                if not keyword:
                    continue
                    
                # 检查关键词是否存在
                keyword_id = current_keyword_map.get(keyword)
                
                if not keyword_id:
                    # 查找是否是其他文档中的关键词
                    keyword_row = query_db(
                        "SELECT keyword_id FROM keyword WHERE keyword_name = %s AND user_id = %s",
                        (keyword, user_id),
                        one=True
                    )
                    
                    if keyword_row:
                        keyword_id = keyword_row['keyword_id']
                        print(f"找到现有关键词: keyword_id = {keyword_id}, name = {keyword}")
                    else:
                        # 创建新关键词
                        keyword_id = query_db(
                            "INSERT INTO keyword (keyword_name, user_id) VALUES (%s, %s)",
                            (keyword, user_id),
                            commit=True
                        )
                        print(f"创建新关键词: keyword_id = {keyword_id}, name = {keyword}")
                
                # 创建文档-关键词关联
                print(f"创建文档-关键词关联: document_id = {document_id}, keyword_id = {keyword_id}")
                query_db(
                    "INSERT INTO document_keyword (document_id, keyword_id) VALUES (%s, %s)",
                    (document_id, keyword_id),
                    commit=True
                )
            
            # 清理未使用的关键词
            for keyword, keyword_id in current_keyword_map.items():
                if keyword not in data.get('keywords', []):
                    # 检查关键词是否还被其他文档引用
                    keyword_check = query_db(
                        """SELECT COUNT(*) as doc_count 
                           FROM document_keyword 
                           WHERE keyword_id = %s""",
                        (keyword_id,),
                        one=True
                    )
                    
                    # 如果没有其他文档引用此关键词，删除关键词
                    if keyword_check and keyword_check['doc_count'] == 0:
                        print(f"删除未使用关键词: keyword_id = {keyword_id}, name = {keyword}")
                        query_db(
                            "DELETE FROM keyword WHERE keyword_id = %s",
                            (keyword_id,),
                            commit=True
                        )
        
        return jsonify({
            "code": 0,
            "message": "文档元数据更新成功"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"更新文档元数据失败: {e}")
        return jsonify({"error": "ServerError", "message": f"更新文档元数据失败: {str(e)}"}), 500

# 辅助函数: 清理未使用的作者
def clean_unused_author(author_id, user_id):
    """
    检查并清理未被任何文档引用的作者
    如果作者不再被任何文档引用，则删除作者和相关的作者-机构关联
    """
    # 检查作者是否还被其他文档引用
    author_check = query_db(
        "SELECT COUNT(*) as doc_count FROM document_author WHERE author_id = %s",
        (author_id,),
        one=True
    )
    
    # 如果没有其他文档引用此作者
    if author_check and author_check['doc_count'] == 0:
        print(f"作者未被引用，准备清理: author_id = {author_id}")
        
        # 获取作者关联的所有机构
        institutions = query_db(
            "SELECT institution_id FROM author_institution WHERE author_id = %s",
            (author_id,)
        )
        institution_ids = [i['institution_id'] for i in institutions]
        
        # 删除作者-机构关联
        if institution_ids:
            print(f"删除作者-机构关联: author_id = {author_id}")
            query_db(
                "DELETE FROM author_institution WHERE author_id = %s",
                (author_id,),
                commit=True
            )
        
        # 删除作者
        print(f"删除作者: author_id = {author_id}")
        query_db(
            "DELETE FROM author WHERE author_id = %s",
            (author_id,),
            commit=True
        )
        
        # 检查每个机构是否还有其他作者关联
        for inst_id in institution_ids:
            inst_check = query_db(
                "SELECT COUNT(*) as author_count FROM author_institution WHERE institution_id = %s",
                (inst_id,),
                one=True
            )
            
            # 如果机构不再有任何作者关联，删除机构
            if inst_check and inst_check['author_count'] == 0:
                print(f"机构未被引用，删除机构: institution_id = {inst_id}")
                query_db(
                    "DELETE FROM institution WHERE institution_id = %s",
                    (inst_id,),
                    commit=True
                )

# 辅助函数: 清理未使用的关键词
def clean_unused_keyword(keyword_id, user_id):
    """
    检查并清理未被任何文档引用的关键词
    如果关键词不再被任何文档引用，则删除关键词
    """
    # 检查关键词是否还被其他文档引用
    keyword_check = query_db(
        "SELECT COUNT(*) as doc_count FROM document_keyword WHERE keyword_id = %s",
        (keyword_id,),
        one=True
    )
    
    # 如果没有其他文档引用此关键词，删除它
    if keyword_check and keyword_check['doc_count'] == 0:
        print(f"关键词未被引用，删除关键词: keyword_id = {keyword_id}")
        query_db(
            "DELETE FROM keyword WHERE keyword_id = %s",
            (keyword_id,),
            commit=True
        )
