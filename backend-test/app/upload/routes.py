import os
import json
import pandas as pd
from flask import request, jsonify, current_app, g, make_response
from werkzeug.utils import secure_filename
import traceback
import uuid

from . import upload_bp
from app.db import query_db, get_db, close_db
from app.utils.decorators import login_required

@upload_bp.route('/metadata-only', methods=['POST'])
@login_required
def save_metadata_only():
    """保存元数据，不保存PDF"""
    try:
        data = request.json
        print(f"收到元数据保存请求: {data}")

        if 'metadataList' in data:
            # 新格式，适配处理
            metadata_items = data.get('metadataList', [])
            folder_id = data.get('folderId')
        else:
            # 旧格式，直接使用
            metadata_items = data.get('metadata', [])
            folder_id = data.get('folderId')

        user_id = g.current_user['user_id']

        if not metadata_items:
            return jsonify({"error": "无效的元数据列表", "message": "请提供有效的元数据数组"}), 400

        # 提取实际的元数据信息
        metadata_list = []
        for item in metadata_items:
            if isinstance(item, dict) and 'metadata' in item:
                # 新格式，提取嵌套metadata
                metadata_list.append(item)
            else:
                # 旧格式，直接添加
                metadata_list.append(item)

        if not metadata_list:
            return jsonify({"error": "无效的元数据内容", "message": "无法从提供的数据中提取有效的元数据信息"}), 400

        if not folder_id:
            return jsonify({"error": "缺少文件夹ID", "message": "请指定保存元数据的目标文件夹"}), 400

        # 验证文件夹是否存在且属于该用户
        folder_check = query_db("SELECT directory_id FROM directory WHERE directory_id = %s AND user_id = %s",
                                (folder_id, user_id), one=True)

        if not folder_check:
            return jsonify({"error": "文件夹不存在或无访问权限", "message": "请选择一个有效的文件夹"}), 400

        # 获取数据库连接和游标
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        saved_count = 0
        failed_count = 0
        messages = []

        # 处理每条元数据
        for item in metadata_list:
            try:
                metadata = item.get('metadata', {})

                title = metadata.get('title', '')
                authors = metadata.get('authors', [])
                sequence = metadata.get('sequence', [])
                institutions = metadata.get('institutions', [])
                institution_locations = metadata.get('institution_location', [])
                emails = metadata.get('email', [])
                doi = metadata.get('doi')
                publish_date = metadata.get('publishDate') or metadata.get('publication_date')
                journal = metadata.get('journal')
                journal_issue = metadata.get('journal_issue')
                conference = metadata.get('conference')
                conference_time = metadata.get('conference_time')
                conference_location = metadata.get('conference_location')
                keywords = metadata.get('keywords', [])
                local_url = metadata.get('local_url', '')

                print("email:", emails)

                # 检查标题是否为空
                if not title:
                    messages.append(f"文件 '{item.get('fileName', '未知')}' 缺少标题")
                    failed_count += 1
                    continue

                # 判断当前folder下是否有同名文档
                cursor.execute("""
                    SELECT document_id FROM document
                    WHERE directory_id = %s AND user_id = %s AND title = %s
                """, (folder_id, user_id, title))
                existing_doc = cursor.fetchone()
                if existing_doc:
                    messages.append(f"文件 '{item.get('fileName', '未知')}' 已存在于当前文件夹中")
                    failed_count += 1
                    continue


                # 处理容器信息 (期刊或会议)
                container_id = None
                if journal:
                    # 查找已有期刊或创建新的
                    cursor.execute("""
                        SELECT container_id FROM container 
                        WHERE container_name = %s AND type = 'journal' AND user_id = %s AND journal_issue = %s
                    """, (journal, user_id, journal_issue))

                    container_result = cursor.fetchone()

                    if container_result:
                        print(f"找到现有期刊: {journal}")
                        container_id = container_result['container_id']

                        # # 更新期刊期号
                        # if journal_issue:
                        #     cursor.execute("""
                        #         UPDATE container SET journal_issue = %s 
                        #         WHERE container_id = %s AND user_id = %s
                        #     """, (journal_issue, container_id, user_id))
                        #     conn.commit()  # 确保每次更新后提交事务
                    else:
                        # 创建新期刊
                        cursor.execute("""
                            INSERT INTO container (container_name, type, journal_issue, user_id) 
                            VALUES (%s, 'journal', %s, %s)
                        """, (journal, journal_issue, user_id))
                        conn.commit()  # 提交创建新期刊的事务

                        # 获取新创建的期刊ID
                        cursor.execute("SELECT LAST_INSERT_ID() AS container_id")
                        container_id = cursor.fetchone()['container_id']

                elif conference:
                    # 查找已有会议或创建新的
                    cursor.execute("""
                        SELECT container_id FROM container 
                        WHERE container_name = %s AND type = 'conference' AND user_id = %s AND conference_location = %s AND conference_time = %s
                    """, (conference, user_id, conference_location, conference_time))

                    container_result = cursor.fetchone()

                    if container_result:
                        container_id = container_result['container_id']

                        # 更新会议信息
                        # if conference_time or conference_location:
                        #     cursor.execute("""
                        #         UPDATE container SET 
                        #         conference_time = COALESCE(%s, conference_time),
                        #         conference_location = COALESCE(%s, conference_location)
                        #         WHERE container_id = %s AND user_id = %s
                        #     """, (conference_time, conference_location, container_id, user_id))
                        #     conn.commit()  # 确保每次更新后提交事务
                    else:
                        # 创建新会议
                        cursor.execute("""
                            INSERT INTO container (container_name, type, conference_time, conference_location, user_id) 
                            VALUES (%s, 'conference', %s, %s, %s)
                        """, (conference, conference_time, conference_location, user_id))
                        conn.commit()  # 提交创建新会议的事务

                        # 获取新创建的会议ID
                        cursor.execute("SELECT LAST_INSERT_ID() AS container_id")
                        container_id = cursor.fetchone()['container_id']

                # 创建文档
                cursor.execute("""
                    INSERT INTO document (directory_id, container_id, user_id, title, doi, publication_date, local_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (folder_id, container_id, user_id, title, doi, publish_date, local_url))
                conn.commit()  # 提交创建文档的事务

                # 获取新创建的文档ID
                cursor.execute("SELECT LAST_INSERT_ID() AS document_id")
                document_id = cursor.fetchone()['document_id']

                # 处理作者、机构和关键字
                if document_id:
                    # 处理作者和机构
                    for i, author_name in enumerate(authors):
                        if not author_name.strip():
                            continue

                        author_sequence = sequence[i] if i < len(sequence) else None
                        author_email = emails[i] if i < len(emails) else None
                        institution_name = institutions[i] if i < len(institutions) else None
                        institution_location = institution_locations[i] if i < len(institution_locations) else None

                        # 查找或创建作者
                        cursor.execute("""
                            SELECT author_id FROM author 
                            WHERE author_name = %s AND user_id = %s
                        """, (author_name, user_id))

                        author_result = cursor.fetchone()

                        if author_result:
                            author_id = author_result['author_id']
                            print(f"找到现有作者: {author_name}, author_id = {author_id}")

                            # 更新作者邮箱如果提供了新的
                            if author_email:
                                cursor.execute("""
                                    UPDATE author SET author_email = %s 
                                    WHERE author_id = %s AND user_id = %s
                                """, (author_email, author_id, user_id))
                                conn.commit()  # 提交更新
                        else:
                            # 创建新作者
                            print(f"未找到现有作者，创建新作者: {author_name}, email = {author_email}")
                            cursor.execute("""
                                INSERT INTO author (author_name, author_email, user_id)
                                VALUES (%s, %s, %s)
                            """, (author_name, author_email, user_id))
                            conn.commit()  # 提交创建作者事务

                            # 获取新创建的作者ID
                            cursor.execute("SELECT LAST_INSERT_ID() AS author_id")
                            author_id = cursor.fetchone()['author_id']

                        # 处理机构
                        institution_id = None
                        if institution_name:
                            cursor.execute("""
                                SELECT institution_id FROM institution
                                WHERE institution_name = %s AND user_id = %s
                            """, (institution_name, user_id))

                            institution_result = cursor.fetchone()

                            if institution_result:
                                institution_id = institution_result['institution_id']
                                print(f"找到现有机构: {institution_name}, institution_id = {institution_id}")

                                # 更新机构位置如果提供了新的
                                if institution_location:
                                    cursor.execute("""
                                        UPDATE institution SET institution_location = %s
                                        WHERE institution_id = %s AND user_id = %s
                                    """, (institution_location, institution_id, user_id))
                                    conn.commit()  # 提交更新
                            else:
                                # 创建新机构
                                print(f"未找到现有机构，创建新机构: {institution_name}, location = {institution_location}")
                                cursor.execute("""
                                    INSERT INTO institution (institution_name, institution_location, user_id)
                                    VALUES (%s, %s, %s)
                                """, (institution_name, institution_location, user_id))
                                conn.commit()  # 提交创建机构事务

                                # 获取新创建的机构ID
                                cursor.execute("SELECT LAST_INSERT_ID() AS institution_id")
                                institution_id = cursor.fetchone()['institution_id']

                        # 创建文档-作者关联
                        print(f"创建文档-作者关联: document_id = {document_id}, author_id = {author_id}, institution_id = {institution_id}, sequence = {author_sequence}")
                        cursor.execute("""
                            INSERT INTO document_author (document_id, author_id, institution_id, sequence)
                            VALUES (%s, %s, %s, %s)
                        """, (document_id, author_id, institution_id, author_sequence))
                        conn.commit()  # 提交创建关联事务
                        # 附带创建作者-机构关联

                        # 先检查是否已有作者机构关联
                        cursor.execute("""
                            SELECT 1 FROM author_institution
                            WHERE author_id = %s AND institution_id = %s
                        """, (author_id, institution_id))
                        existing_relation = cursor.fetchone()

                        if not existing_relation:
                            print(f"创建新的作者-机构关联: author_id = {author_id}, institution_id = {institution_id}")
                            cursor.execute("""
                                INSERT INTO author_institution (author_id, institution_id)
                                VALUES (%s, %s)
                            """, (author_id, institution_id))
                            conn.commit()  # 提交作者-机构关联事务

                    # 处理关键字
                    for keyword in keywords:
                        if not keyword.strip():
                            continue

                        # 查找或创建关键字
                        cursor.execute("""
                            SELECT keyword_id FROM keyword
                            WHERE keyword_name = %s AND user_id = %s
                        """, (keyword, user_id))

                        keyword_result = cursor.fetchone()

                        if keyword_result:
                            print(f"找到现有关键字: {keyword}, keyword_id = {keyword_result['keyword_id']}")
                            keyword_id = keyword_result['keyword_id']
                        else:
                            # 创建新关键字
                            cursor.execute("""
                                INSERT INTO keyword (keyword_name, user_id)
                                VALUES (%s, %s)
                            """, (keyword, user_id))
                            conn.commit()  # 提交创建关键字事务

                            # 获取新创建的关键字ID
                            cursor.execute("SELECT LAST_INSERT_ID() AS keyword_id")
                            keyword_id = cursor.fetchone()['keyword_id']

                        # 创建文档-关键字关联
                        cursor.execute("""
                            INSERT INTO document_keyword (document_id, keyword_id)
                            VALUES (%s, %s)
                        """, (document_id, keyword_id))
                        conn.commit()  # 提交创建关联事务

                saved_count += 1

            except Exception as e:
                conn.rollback()  # 出错时回滚
                failed_count += 1
                error_message = f"处理元数据时出错: {str(e)}"
                messages.append(f"文件 '{item.get('fileName', '未知')}': {error_message}")
                current_app.logger.error(f"元数据处理错误: {e}")
                continue

        # 关闭游标
        cursor.close()

        # 构建响应消息
        result_message = f"成功处理 {saved_count} 条元数据"
        if failed_count > 0:
            result_message += f", {failed_count} 条处理失败"

        if messages:
            detailed_messages = "; ".join(messages)
            result_message += f". 详细信息: {detailed_messages}"

        return jsonify({
            "code": 0,
            "message": result_message,
            "data": {
                "totalProcessed": len(metadata_list),
                "succeeded": saved_count,
                "failed": failed_count,
                "messages": messages
            }
        })

    except Exception as e:
        current_app.logger.error(f"[save_metadata_only] 详细错误: {e}", exc_info=True)
        return jsonify({"error": "服务器错误", "message": f"保存元数据失败: {str(e)}"}), 500

@upload_bp.route('/metadata', methods=['POST'])
@login_required
def upload_metadata():
    """批量导入元数据（前端已完成解析）"""
    try:
        print("\n==== 开始处理元数据批量导入请求 ====")
        data = request.json
        if not data:
            print("错误: 请求中未包含JSON数据")
            return jsonify({"error": "数据格式错误", "message": "请求中未包含JSON数据"}), 400

        # 获取必要参数
        metadata_list = data.get('metadataList', [])
        folder_id = data.get('folderId')
        user_id = g.current_user['user_id']

        print(f"收到请求参数: folder_id={folder_id}, user_id={user_id}")
        print(f"元数据列表长度: {len(metadata_list)}")

        if not metadata_list:
            print("错误: 元数据列表为空")
            return jsonify({"error": "数据格式错误", "message": "元数据列表为空"}), 400

        if not folder_id:
            print("错误: 未提供文件夹ID")
            return jsonify({"error": "参数错误", "message": "必须提供文件夹ID"}), 400

        current_app.logger.info(f"导入元数据，记录数: {len(metadata_list)}")
        print(f"导入元数据，记录数: {len(metadata_list)}")

        # 验证文件夹归属
        print(f"SQL: 验证文件夹归属 SELECT directory_id FROM directory WHERE directory_id = {folder_id} AND user_id = {user_id}")
        folder = query_db("SELECT directory_id FROM directory WHERE directory_id = %s AND user_id = %s",
                          (folder_id, user_id), one=True)

        if not folder:
            print(f"错误: 文件夹不存在或无权访问, folder_id={folder_id}, user_id={user_id}")
            return jsonify({"error": "权限错误", "message": "文件夹不存在或无权访问"}), 404

        print(f"文件夹验证成功: {folder}")

        imported_count = 0
        failed_count = 0

        # 处理每条元数据记录
        for index, metadata in enumerate(metadata_list):
            try:
                print(f"\n---- 开始处理第 {index+1}/{len(metadata_list)} 条元数据 ----")
                print(f"元数据内容: {json.dumps(metadata, ensure_ascii=False)[:200]}...")

                # 从元数据中提取必要信息
                title = metadata.get('title')
                if not title:  # 跳过没有标题的记录
                    print(f"跳过记录 {index+1}: 缺少标题")
                    failed_count += 1
                    continue

                # 提取基本字段
                doi = metadata.get('doi')
                publish_date = metadata.get('publishDate') or metadata.get('publication_date')
                local_url = metadata.get('local_url', '')

                # 先处理容器（期刊/会议）
                container_id = None
                container_name = None
                container_type = None

                if metadata.get('journal'):
                    container_name = metadata.get('journal')
                    container_type = "journal"
                    journal_issue = metadata.get('journal_issue')
                    print(f"检测到期刊: {container_name}, issue: {journal_issue}")
                elif metadata.get('conference'):
                    container_name = metadata.get('conference')
                    container_type = "conference"
                    conference_time = metadata.get('conference_time')
                    conference_location = metadata.get('conference_location')
                    print(f"检测到会议: {container_name}, time: {conference_time}, location: {conference_location}")

                # 如果有容器信息，查找或创建容器
                if container_name and container_type:
                    print(f"处理容器信息: name={container_name}, type={container_type}")

                    container_search_sql = "SELECT container_id FROM container WHERE container_name = %s AND user_id = %s AND type = %s"
                    print(f"SQL: 查找容器 - {container_search_sql}")
                    print(f"SQL参数: ({container_name}, {user_id}, {container_type})")

                    container_result = query_db(
                        container_search_sql,
                        (container_name, user_id, container_type),
                        one=True
                    )

                    if not container_result:
                        container_create_sql = """INSERT INTO container (container_name, user_id, type, journal_issue, 
                               conference_time, conference_location) 
                               VALUES (%s, %s, %s, %s, %s, %s)"""

                        journal_issue = metadata.get('journal_issue') if container_type == "journal" else None
                        conference_time = metadata.get('conference_time') if container_type == "conference" else None
                        conference_location = metadata.get('conference_location') if container_type == "conference" else None

                        print(f"SQL: 创建容器 - {container_create_sql}")
                        print(f"SQL参数: ({container_name}, {user_id}, {container_type}, {journal_issue}, {conference_time}, {conference_location})")

                        container_id = query_db(
                            container_create_sql,
                            (container_name, user_id, container_type,
                             journal_issue, conference_time,
                             conference_location),
                            commit=True
                        )
                        print(f"容器创建成功，container_id = {container_id}")
                    else:
                        container_id = container_result['container_id']
                        print(f"找到现有容器，container_id = {container_id}")

                # 创建文档记录 - 更新插入语句，使用container_id
                insert_doc_sql = """INSERT INTO document 
                       (directory_id, user_id, title, doi, publication_date, container_id, local_url)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""

                print(f"SQL: 创建文档记录 - {insert_doc_sql}")
                print(f"SQL参数: ({folder_id}, {user_id}, {title}, {doi}, {publish_date}, {container_id}, {local_url})")

                document_id = query_db(
                    insert_doc_sql,
                    (folder_id, user_id, title, doi, publish_date, container_id, local_url),
                    commit=True
                )

                print(f"文档记录创建成功，document_id = {document_id}")

                # 处理作者 (如果存在)
                authors = metadata.get('authors', [])
                if isinstance(authors, list) and authors:
                    print(f"处理作者信息, 作者数: {len(authors)}")
                    for i, author_name in enumerate(authors):
                        if not author_name:
                            print(f"跳过空作者名，索引: {i}")
                            continue

                        # 获取其他作者相关字段
                        sequence = metadata.get('sequence', [])[i] if i < len(metadata.get('sequence', [])) else "additional"
                        institution_name = metadata.get('institutions', [])[i] if i < len(metadata.get('institutions', [])) else None
                        location = metadata.get('institution_location', [])[i] if i < len(metadata.get('institution_location', [])) else None
                        email = metadata.get('email', [])[i] if i < len(metadata.get('email', [])) else None

                        # 查找或创建作者 - 修改为同时更新邮箱
                        author_search_sql = "SELECT author_id FROM author WHERE author_name = %s AND user_id = %s"
                        print(f"SQL: 查找作者 - {author_search_sql}")
                        print(f"SQL参数: ({author_name}, {user_id})")

                        author_id = query_db(
                            author_search_sql,
                            (author_name, user_id),
                            one=True
                        )

                        if not author_id:
                            # 创建新作者，包含邮箱信息
                            author_create_sql = "INSERT INTO author (author_name, user_id, author_email) VALUES (%s, %s, %s)"
                            print(f"SQL: 创建作者(含邮箱) - {author_create_sql}")
                            print(f"SQL参数: ({author_name}, {user_id}, {email})")

                            author_id = query_db(
                                author_create_sql,
                                (author_name, user_id, email),
                                commit=True
                            )
                            print(f"作者创建成功，author_id = {author_id}")
                        else:
                            author_id = author_id['author_id']
                            print(f"找到现有作者，author_id = {author_id}")

                            # 如果有邮箱信息，更新现有作者的邮箱
                            if email:
                                author_update_sql = "UPDATE author SET author_email = %s WHERE author_id = %s AND user_id = %s"
                                print(f"SQL: 更新作者邮箱 - {author_update_sql}")
                                print(f"SQL参数: ({email}, {author_id}, {user_id})")

                                query_db(
                                    author_update_sql,
                                    (email, author_id, user_id),
                                    commit=True
                                )
                                print(f"作者邮箱更新成功: email = {email}")

                        # 查找或创建机构，获取机构ID
                        institution_id = None
                        if institution_name:
                            institution_search_sql = "SELECT institution_id, institution_location FROM institution WHERE institution_name = %s AND user_id = %s"
                            print(f"SQL: 查找机构 - {institution_search_sql}")
                            print(f"SQL参数: ({institution_name}, {user_id})")

                            institution_result = query_db(
                                institution_search_sql,
                                (institution_name, user_id),
                                one=True
                            )

                            if not institution_result:
                                # 创建新机构
                                institution_create_sql = "INSERT INTO institution (institution_name, institution_location, user_id) VALUES (%s, %s, %s)"
                                print(f"SQL: 创建机构 - {institution_create_sql}")
                                print(f"SQL参数: ({institution_name}, {location}, {user_id})")

                                institution_id = query_db(
                                    institution_create_sql,
                                    (institution_name, location, user_id),
                                    commit=True
                                )
                                print(f"机构创建成功，institution_id = {institution_id}")
                            else:
                                institution_id = institution_result['institution_id']
                                print(f"找到现有机构，institution_id = {institution_id}")

                                # 如果元数据中提供了新的地址信息，则更新机构地址
                                # location comes from metadata.get('institution_location', [])[i]
                                if location is not None: # Check if location is explicitly provided in input
                                    # Only update if the new location is different or if you always want to overwrite
                                    if location != institution_result.get('institution_location'):
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

                            # 检查作者-机构关联是否已存在，若不存在则添加
                            if institution_id and author_id:
                                # 查询是否已存在关联
                                author_institution_check_sql = """
                                SELECT 1 FROM author_institution 
                                WHERE author_id = %s AND institution_id = %s"""
                                print(f"SQL: 检查作者-机构关联 - {author_institution_check_sql}")
                                print(f"SQL参数: ({author_id}, {institution_id})")

                                existing_relation = query_db(
                                    author_institution_check_sql,
                                    (author_id, institution_id),
                                    one=True
                                )

                                # 如果关联不存在，创建新的关联
                                if not existing_relation:
                                    author_institution_sql = """
                                    INSERT INTO author_institution (author_id, institution_id) 
                                    VALUES (%s, %s)"""
                                    print(f"SQL: 创建作者-机构关联 - {author_institution_sql}")
                                    print(f"SQL参数: ({author_id}, {institution_id})")

                                    query_db(
                                        author_institution_sql,
                                        (author_id, institution_id),
                                        commit=True
                                    )
                                    print(f"作者-机构关联创建成功: author_id={author_id}, institution_id={institution_id}")
                                else:
                                    print(f"作者-机构关联已存在: author_id={author_id}, institution_id={institution_id}")

                        print(f"作者 {i+1} ({author_name}) 详细信息: sequence={sequence}, institution_id={institution_id}, location={location}, email={email}")

                        # 关联作者与文档 - 修改为不再传递email参数，因为email已存储在author表中
                        doc_author_sql = """INSERT INTO document_author 
                               (document_id, author_id, sequence, institution_id) 
                               VALUES (%s, %s, %s, %s)"""

                        print(f"SQL: 关联作者与文档 - {doc_author_sql}")
                        print(f"SQL参数: ({document_id}, {author_id}, {sequence}, {institution_id})")

                        query_db(
                            doc_author_sql,
                            (document_id, author_id, sequence, institution_id),
                            commit=True
                        )
                        print(f"作者 {author_name} 与文档关联成功")

                # 处理关键词 (如果存在)
                keywords = metadata.get('keywords', [])
                if isinstance(keywords, list) and keywords:
                    print(f"处理关键词信息, 关键词数: {len(keywords)}")
                    for keyword in keywords:
                        if not keyword:
                            print("跳过空关键词")
                            continue

                        # 查找或创建关键词
                        keyword_search_sql = "SELECT keyword_id FROM keyword WHERE keyword_name = %s AND user_id = %s"
                        print(f"SQL: 查找关键词 - {keyword_search_sql}")
                        print(f"SQL参数: ({keyword}, {user_id})")

                        keyword_id = query_db(
                            keyword_search_sql,
                            (keyword, user_id),
                            one=True
                        )

                        if not keyword_id:
                            keyword_create_sql = "INSERT INTO keyword (keyword_name, user_id) VALUES (%s, %s)"
                            print(f"SQL: 创建关键词 - {keyword_create_sql}")
                            print(f"SQL参数: ({keyword}, {user_id})")

                            keyword_id = query_db(
                                keyword_create_sql,
                                (keyword, user_id),
                                commit=True
                            )
                            print(f"关键词创建成功，keyword_id = {keyword_id}")
                        else:
                            keyword_id = keyword_id['keyword_id']
                            print(f"找到现有关键词，keyword_id = {keyword_id}")

                        # 关联关键词与文档
                        doc_keyword_sql = "INSERT INTO document_keyword (document_id, keyword_id) VALUES (%s, %s)"
                        print(f"SQL: 关联关键词与文档 - {doc_keyword_sql}")
                        print(f"SQL参数: ({document_id}, {keyword_id})")

                        query_db(
                            doc_keyword_sql,
                            (document_id, keyword_id),
                            commit=True
                        )
                        print(f"关键词 {keyword} 与文档关联成功")

                imported_count += 1
                print(f"---- 第 {index+1} 条元数据处理完成 ----")

            except Exception as e:
                print(f"处理第 {index+1} 条元数据时出错: {str(e)}")
                current_app.logger.error(f"导入元数据记录错误: {e}")
                failed_count += 1
                # 继续处理下一条记录

        print(f"\n==== 元数据批量导入完成 ====")
        print(f"成功导入: {imported_count} 条")
        print(f"导入失败: {failed_count} 条")

        if imported_count == 0:
            print("错误: 没有成功导入任何元数据记录")
            return jsonify({
                "code": 1,
                "message": "没有成功导入任何元数据记录",
                "data": {
                    "importedCount": 0,
                    "failedCount": failed_count
                }
            }), 400

        return jsonify({
            "code": 0,
            "message": f"成功导入 {imported_count} 条元数据记录",
            "data": {
                "importedCount": imported_count,
                "failedCount": failed_count
            }
        }), 200

    except Exception as e:
        print(f"批量导入元数据过程中发生异常: {str(e)}")
        current_app.logger.error(f"批量导入元数据失败: {e}")
        return jsonify({"error": "服务器错误", "message": f"处理元数据时出错: {str(e)}"}), 500