import os
import json
import pandas as pd
from flask import request, jsonify, current_app, g, make_response
from werkzeug.utils import secure_filename
import traceback

from . import upload_bp
from app.db import query_db, get_db, close_db
from app.utils.decorators import login_required

# 确保 OPTIONS 处理器在路由顶部定义，并且正确处理预检请求
@upload_bp.route('/<path:path>', methods=['OPTIONS'])
@upload_bp.route('/', methods=['OPTIONS'])
def handle_options_request(*args, **kwargs):
    """处理所有OPTIONS请求"""
    print(f"处理OPTIONS请求: path={kwargs.get('path', '/')} args={args}")
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')  # 缓存预检响应1小时
    response.status_code = 200
    return response

# 确保/metadata路由也能处理OPTIONS请求
@upload_bp.route('/metadata', methods=['OPTIONS'])
def metadata_options():
    """专门处理/metadata的OPTIONS请求"""
    print("处理/metadata OPTIONS请求")
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    response.status_code = 200
    return response

@upload_bp.route('/metadata-only', methods=['POST'])
@login_required
def save_metadata_only():
    user_id = g.current_user['user_id']
    data = request.json

    # 增加调试日志
    print(f"[save_metadata_only] 收到请求 - user_id={user_id}")
    print(f"[save_metadata_only] 请求数据: {data}")

    if not data:
        print("warning:[save_metadata_only] 请求体为空")
        return jsonify({"error": "参数错误", "message": "请求缺少必要参数"}), 400

    folder_id = data.get('folderId')
    metadata_list = data.get('metadataList', [])

    print(f"[save_metadata_only] folderId={folder_id}, metadataList类型={type(metadata_list)}, 长度={len(metadata_list)}")

    if not folder_id:
        print("warning:[save_metadata_only] 没有提供folderId")
        return jsonify({"error": "参数错误", "message": "必须提供文件夹ID"}), 400

    # 尝试将folder_id转为int
    try:
        folder_id_int = int(folder_id)
        print(f"[save_metadata_only] folderId转换成功: {folder_id_int}")
    except Exception as e:
        current_app.logger.error(f"[save_metadata_only] folderId转换失败: {folder_id}, 错误: {e}")
        return jsonify({"error": "参数错误", "message": "文件夹ID必须为数字"}), 400

    if not isinstance(metadata_list, list) or len(metadata_list) == 0:
        print("[save_metadata_only] metadataList不是有效的数组或为空")
        return jsonify({"error": "参数错误", "message": "必须提供元数据列表"}), 400

    # 检查文件夹是否存在且属于当前用户
    folder = query_db("""
        SELECT directory_id FROM directory
        WHERE directory_id = %s AND user_id = %s
    """, (folder_id_int, user_id), one=True)

    if not folder:
        print(f"==db:[save_metadata_only] 找不到文件夹或权限不足: folderId={folder_id_int}, user_id={user_id}")
        return jsonify({"error": "参数错误", "message": "指定的文件夹不存在或无权访问"}), 404

    print(f"==db[save_metadata_only] 文件夹验证通过: {folder_id_int}, 开始处理{len(metadata_list)}个元数据项")

    # 处理上传的元数据
    document_ids = []
    file_names = []

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        print("==db[save_metadata_only] 成功获取数据库连接")
        
        for index, item in enumerate(metadata_list):
            file_name = item.get('fileName', 'unknown.pdf')
            metadata = item.get('metadata', {})
            
            print(f"[save_metadata_only] 处理第{index+1}项: file_name={file_name}")
            
            if not metadata or 'title' not in metadata:
                print(f"[save_metadata_only] 第{index+1}项缺少有效元数据或标题")
                continue
                
            try:
                conn.start_transaction()
                print(f"==db[save_metadata_only] 第{index+1}项: 开始事务")
                
                title = metadata.get('title')
                doi = metadata.get('doi')
                publish_date = metadata.get('publishDate')
                journal_name = metadata.get('journal')
                conference_name = metadata.get('conference')
                
                print(f"==db[save_metadata_only] 第{index+1}项: title={title}, doi={doi}, 出版日期={publish_date}, journal={journal_name}, conference={conference_name}")
                
                container_id = None
                if journal_name or conference_name:
                    container_type = 'journal' if journal_name else 'conference'
                    container_name = journal_name or conference_name
                    
                    print(f"[save_metadata_only] 第{index+1}项: 查询容器 type={container_type}, name={container_name}")
                    
                    cursor.execute("""
                        SELECT container_id FROM container
                        WHERE user_id = %s AND type = %s AND container_name = %s
                    """, (user_id, container_type, container_name))
                    
                    container_result = cursor.fetchone()
                    if container_result:
                        container_id = container_result['container_id']
                        print(f"[save_metadata_only] 第{index+1}项: 找到现有容器, id={container_id}")
                    else:
                        print(f"[save_metadata_only] 第{index+1}项: 创建新容器, type={container_type}, name={container_name}")
                        if container_type == 'journal':
                            cursor.execute("""
                                INSERT INTO container (user_id, type, container_name, journal_issue)
                                VALUES (%s, %s, %s, %s)
                            """, (user_id, container_type, container_name, "Vol. 1"))
                        else:
                            cursor.execute("""
                                INSERT INTO container (user_id, type, container_name, conference_time)
                                VALUES (%s, %s, %s, %s)
                            """, (user_id, container_type, container_name, publish_date or "2023-01-01"))
                        
                        container_id = cursor.lastrowid
                        print(f"[save_metadata_only] 第{index+1}项: 创建容器成功, id={container_id}")
                
                # 创建文档记录
                print(f"[save_metadata_only] 第{index+1}项: 插入文档记录 folder_id={folder_id_int}, container_id={container_id}")
                cursor.execute("""
                    INSERT INTO document (directory_id, container_id, user_id, title, doi, publication_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (folder_id_int, container_id, user_id, title, doi, publish_date))
                
                document_id = cursor.lastrowid
                print(f"[save_metadata_only] 第{index+1}项: 文档创建成功, id={document_id}")
                
                # 处理作者信息
                authors = metadata.get('authors', [])
                if isinstance(authors, list) and authors:
                    print(f"[save_metadata_only] 第{index+1}项: 处理{len(authors)}个作者")
                    for i, author_name in enumerate(authors):
                        if not author_name:
                            print(f"[save_metadata_only] 第{index+1}项: 跳过空作者名称")
                            continue
                        
                        # 获取作者相关信息
                        sequence = metadata.get('sequence', [])[i] if i < len(metadata.get('sequence', [])) else None
                        institution = metadata.get('institutions', [])[i] if i < len(metadata.get('institutions', [])) else None
                        location = metadata.get('institution_location', [])[i] if i < len(metadata.get('institution_location', [])) else None
                        email = metadata.get('email', [])[i] if i < len(metadata.get('email', [])) else None
                        
                        print(f"[save_metadata_only] 第{index+1}项, 作者{i+1}: name={author_name}, sequence={sequence}, institution={institution}")
                        
                        # 查找或创建作者
                        cursor.execute("""
                            SELECT author_id FROM author
                            WHERE user_id = %s AND author_name = %s
                        """, (user_id, author_name))
                        
                        author_result = cursor.fetchone()
                        if author_result:
                            author_id = author_result['author_id']
                            print(f"[save_metadata_only] 第{index+1}项, 作者{i+1}: 找到现有作者 id={author_id}")
                        else:
                            cursor.execute("""
                                INSERT INTO author (user_id, author_name, author_email)
                                VALUES (%s, %s, %s)
                            """, (user_id, author_name, email))
                            author_id = cursor.lastrowid
                            print(f"[save_metadata_only] 第{index+1}项, 作者{i+1}: 创建新作者 id={author_id}")
                        
                        # 确保sequence为标准值
                        if sequence not in ["first", "corresponding", "additional", "other"]:
                            print(f"[save_metadata_only] 第{index+1}项, 作者{i+1}: sequence值({sequence})不标准, 使用'additional'")
                            sequence = "additional"  # 默认为additional
                        
                        # 创建文档-作者关联
                        cursor.execute("""
                            INSERT INTO document_author (document_id, author_id, sequence)
                            VALUES (%s, %s, %s)
                        """, (document_id, author_id, sequence))
                        print(f"[save_metadata_only] 第{index+1}项, 作者{i+1}: 创建文档-作者关联成功")
                        
                        # 处理机构信息
                        if institution:
                            cursor.execute("""
                                SELECT institution_id FROM institution
                                WHERE user_id = %s AND institution_name = %s
                            """, (user_id, institution))
                            
                            institution_result = cursor.fetchone()
                            if institution_result:
                                institution_id = institution_result['institution_id']
                                print(f"[save_metadata_only] 第{index+1}项, 作者{i+1}: 找到现有机构 id={institution_id}")
                            else:
                                cursor.execute("""
                                    INSERT INTO institution (user_id, institution_name, institution_location)
                                    VALUES (%s, %s, %s)
                                """, (user_id, institution, location))
                                institution_id = cursor.lastrowid
                                print(f"[save_metadata_only] 第{index+1}项, 作者{i+1}: 创建新机构 id={institution_id}")
                        
                            # 检查作者-机构关联是否已存在
                            cursor.execute("""
                                SELECT * FROM author_institution
                                WHERE author_id = %s AND institution_id = %s
                            """, (author_id, institution_id))
                            
                            existing_relation = cursor.fetchone()
                            
                            if existing_relation:
                                print(f"[save_metadata_only] 第{index+1}项, 作者{i+1}: 作者-机构关联已存在")
                            else:
                                # 创建作者-机构关联
                                cursor.execute("""
                                    INSERT INTO author_institution (author_id, institution_id)
                                    VALUES (%s, %s)
                                """, (author_id, institution_id))
                                print(f"[save_metadata_only] 第{index+1}项, 作者{i+1}: 创建作者-机构关联成功")
                
                # 处理关键词信息
                keywords = metadata.get('keywords', [])
                if isinstance(keywords, list) and keywords:
                    print(f"[save_metadata_only] 第{index+1}项: 处理{len(keywords)}个关键词")
                    for keyword_idx, keyword in enumerate(keywords):
                        if not keyword:
                            print(f"[save_metadata_only] 第{index+1}项: 跳过空关键词")
                            continue
                        
                        cursor.execute("""
                            SELECT keyword_id FROM keyword
                            WHERE user_id = %s AND keyword_name = %s
                        """, (user_id, keyword))
                        
                        keyword_result = cursor.fetchone()
                        if keyword_result:
                            keyword_id = keyword_result['keyword_id']
                            print(f"[save_metadata_only] 第{index+1}项, 关键词{keyword_idx+1}: 找到现有关键词 '{keyword}' id={keyword_id}")
                        else:
                            cursor.execute("""
                                INSERT INTO keyword (user_id, keyword_name)
                                VALUES (%s, %s)
                            """, (user_id, keyword))
                            keyword_id = cursor.lastrowid
                            print(f"[save_metadata_only] 第{index+1}项, 关键词{keyword_idx+1}: 创建新关键词 '{keyword}' id={keyword_id}")
                        
                        # 创建文档-关键词关联
                        cursor.execute("""
                            INSERT INTO document_keyword (document_id, keyword_id)
                            VALUES (%s, %s)
                        """, (document_id, keyword_id))
                        print(f"[save_metadata_only] 第{index+1}项, 关键词{keyword_idx+1}: 创建文档-关键词关联成功")
                
                conn.commit()
                print(f"[save_metadata_only] 第{index+1}项: 事务已提交")
                
                # 记录成功处理的项目
                document_ids.append(document_id)
                file_names.append(file_name)
                current_app.logger.info(f"[save_metadata_only] 第{index+1}项: '{title}' 保存成功, document_id={document_id}")
                
            except Exception as e:
                conn.rollback()
                current_app.logger.error(f"[save_metadata_only] 第{index+1}项: 保存元数据失败: {e}")
                current_app.logger.error(f"[save_metadata_only] 详细错误: {traceback.format_exc()}")
    
    except Exception as e:
        current_app.logger.error(f"[save_metadata_only] 处理元数据列表总体失败: {e}")
        current_app.logger.error(f"[save_metadata_only] 详细错误: {traceback.format_exc()}")
        return jsonify({"error": "服务器错误", "message": f"保存元数据失败: {str(e)}"}), 500
    finally:
        close_db()
        print("[save_metadata_only] 数据库连接已关闭")
    
    if not document_ids:
        current_app.logger.warning("[save_metadata_only] 没有成功保存任何元数据记录")
        return jsonify({
            "code": 1,
            "message": "没有成功保存任何元数据记录",
            "data": { "importedCount": 0 }
        }), 400
    
    current_app.logger.info(f"[save_metadata_only] 成功保存 {len(document_ids)} 条元数据记录")
    return jsonify({
        "code": 0,
        "message": f"成功保存 {len(document_ids)} 条元数据记录",
        "data": {
            "docIds": document_ids,
            "fileNames": file_names,
            "importedCount": len(document_ids)
        }
    })

@upload_bp.route('/metadata', methods=['POST'])
@login_required
def upload_metadata_files():
    """批量导入元数据文件 (JSON/XLSX/CSV)"""
    user_id = g.current_user['user_id']
    current_app.logger.info(f"[upload_metadata_files] 收到请求 - user_id={user_id}")
    
    # 检查请求表单和文件
    print(f"[upload_metadata_files] 请求表单: {request.form}")
    print(f"[upload_metadata_files] 请求文件键: {list(request.files.keys())}")
    
    # 检查是否有文件和文件夹ID
    if 'files[0]' not in request.files:
        current_app.logger.warning("[upload_metadata_files] 请求中没有文件 (files[0])")
        return jsonify({"error": "参数错误", "message": "请求中没有文件"}), 400
    
    folder_id = request.form.get('folderId')
    print(f"[upload_metadata_files] folderId={folder_id}")
    
    if not folder_id:
        current_app.logger.warning("[upload_metadata_files] 没有提供folderId")
        return jsonify({"error": "参数错误", "message": "必须提供文件夹ID"}), 400
    
    # 尝试将folder_id转为int
    try:
        folder_id_int = int(folder_id)
        print(f"[upload_metadata_files] folderId转换成功: {folder_id_int}")
    except Exception as e:
        current_app.logger.error(f"[upload_metadata_files] folderId转换失败: {folder_id}, 错误: {e}")
        return jsonify({"error": "参数错误", "message": "文件夹ID必须为数字"}), 400
    
    # 检查文件夹是否存在且属于当前用户
    folder = query_db("""
        SELECT directory_id FROM directory
        WHERE directory_id = %s AND user_id = %s
    """, (folder_id_int, user_id), one=True)
    
    if not folder:
        current_app.logger.warning(f"[upload_metadata_files] 找不到文件夹或权限不足: folderId={folder_id_int}, user_id={user_id}")
        return jsonify({"error": "参数错误", "message": "指定的文件夹不存在或无权访问"}), 404
    
    current_app.logger.info(f"[upload_metadata_files] 文件夹验证通过: {folder_id_int}")
    
    # 获取上传的所有文件
    file_count = 0
    uploaded_files = []
    
    while True:
        file_key = f'files[{file_count}]'
        if file_key not in request.files:
            break
        
        file = request.files[file_key]
        if file and file.filename:
            uploaded_files.append(file)
            print(f"[upload_metadata_files] 收到文件: {file.filename}, 大小: {file.content_length if hasattr(file, 'content_length') else '未知'}")
        else:
            print(f"[upload_metadata_files] 键 {file_key} 存在但没有有效文件名")
        file_count += 1
    
    if not uploaded_files:
        current_app.logger.warning("[upload_metadata_files] 没有有效的文件被上传")
        return jsonify({"error": "参数错误", "message": "没有有效的文件被上传"}), 400
    
    current_app.logger.info(f"[upload_metadata_files] 收到 {len(uploaded_files)} 个文件")
    
    # 处理每个上传的文件
    total_records_imported = 0
    imported_metadata = []
    file_summaries = []
    
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        print("[upload_metadata_files] 成功获取数据库连接")
        
        for file_index, file in enumerate(uploaded_files):
            file_name = file.filename
            current_app.logger.info(f"[upload_metadata_files] 开始处理文件 {file_index+1}/{len(uploaded_files)}: {file_name}")
            
            records_in_this_file = 0
            failed_records_in_this_file = 0
            
            try:
                # 根据文件类型解析元数据
                metadata_records = []
                
                # 解析JSON文件
                if file_name.lower().endswith('.json'):
                    print(f"[upload_metadata_files] 文件 {file_name} 为JSON格式")
                    try:
                        file_content = file.read()
                        file.seek(0)  # 重置文件指针以供后续处理
                        data = json.loads(file_content)
                        
                        # 文件内容调试
                        content_excerpt = file_content[:500] + (b"..." if len(file_content) > 500 else b"")
                        print(f"[upload_metadata_files] JSON内容摘要: {content_excerpt}")
                        
                        # 处理单个对象或对象数组
                        if isinstance(data, dict):
                            metadata_records = [data]
                            print("[upload_metadata_files] JSON为单个对象")
                        elif isinstance(data, list):
                            metadata_records = data
                            print(f"[upload_metadata_files] JSON为对象数组, 长度: {len(data)}")
                        else:
                            current_app.logger.warning(f"[upload_metadata_files] JSON格式无效, 类型: {type(data)}")
                            continue
                    except json.JSONDecodeError as e:
                        current_app.logger.error(f"[upload_metadata_files] JSON解析错误: {e}")
                        continue
                
                # 解析CSV文件
                elif file_name.lower().endswith('.csv'):
                    print(f"[upload_metadata_files] 文件 {file_name} 为CSV格式")
                    try:
                        df = pd.read_csv(file)
                        metadata_records = df.to_dict(orient='records')
                        print(f"[upload_metadata_files] CSV解析成功, 记录数: {len(metadata_records)}")
                    except Exception as e:
                        current_app.logger.error(f"[upload_metadata_files] CSV解析错误: {e}")
                        current_app.logger.error(f"[upload_metadata_files] 详细错误: {traceback.format_exc()}")
                        continue
                
                # 解析Excel文件
                elif file_name.lower().endswith(('.xlsx', '.xls')):
                    print(f"[upload_metadata_files] 文件 {file_name} 为Excel格式")
                    try:
                        df = pd.read_excel(file)
                        metadata_records = df.to_dict(orient='records')
                        print(f"[upload_metadata_files] Excel解析成功, 记录数: {len(metadata_records)}")
                    except Exception as e:
                        current_app.logger.error(f"[upload_metadata_files] Excel解析错误: {e}")
                        current_app.logger.error(f"[upload_metadata_files] 详细错误: {traceback.format_exc()}")
                        continue
                else:
                    # 不支持的文件类型
                    current_app.logger.warning(f"[upload_metadata_files] 文件 {file_name} 格式不支持")
                    continue
                
                # 处理每条元数据记录
                for record_index, record in enumerate(metadata_records):
                    print(f"[upload_metadata_files] 处理文件 {file_name} 中的第 {record_index+1}/{len(metadata_records)} 条记录")
                    try:
                        # 开始事务
                        conn.start_transaction()
                        
                        # 提取基本元数据
                        title = record.get('title')
                        if not title:  # 跳过没有标题的记录
                            current_app.logger.warning(f"[upload_metadata_files] 文件 {file_name} 的第 {record_index+1} 条记录缺少标题, 跳过")
                            conn.rollback()
                            failed_records_in_this_file += 1
                            continue
                            
                        doi = record.get('doi')
                        publish_date = record.get('publishDate')
                        journal_name = record.get('journal')
                        conference_name = record.get('conference')
                        
                        print(f"[upload_metadata_files] 记录 {record_index+1}: title={title}, doi={doi}, 出版日期={publish_date}")
                        
                        # 处理容器信息（期刊或会议）
                        container_id = None
                        if journal_name or conference_name:
                            container_type = 'journal' if journal_name else 'conference'
                            container_name = journal_name or conference_name
                            
                            print(f"[upload_metadata_files] 记录 {record_index+1}: 查询容器 type={container_type}, name={container_name}")
                            
                            cursor.execute("""
                                SELECT container_id FROM container
                                WHERE user_id = %s AND type = %s AND container_name = %s
                            """, (user_id, container_type, container_name))
                            
                            container_result = cursor.fetchone()
                            if container_result:
                                container_id = container_result['container_id']
                                print(f"[upload_metadata_files] 记录 {record_index+1}: 找到现有容器, id={container_id}")
                            else:
                                print(f"[upload_metadata_files] 记录 {record_index+1}: 创建新容器, type={container_type}, name={container_name}")
                                if container_type == 'journal':
                                    cursor.execute("""
                                        INSERT INTO container (user_id, type, container_name, journal_issue)
                                        VALUES (%s, %s, %s, %s)
                                    """, (user_id, container_type, container_name, "Vol. 1"))
                                else:
                                    cursor.execute("""
                                        INSERT INTO container (user_id, type, container_name, conference_time)
                                        VALUES (%s, %s, %s, %s)
                                    """, (user_id, container_type, container_name, publish_date or "2023-01-01"))
                                
                                container_id = cursor.lastrowid
                                print(f"[upload_metadata_files] 记录 {record_index+1}: 创建容器成功, id={container_id}")
                        
                        # 创建文档记录
                        print(f"[upload_metadata_files] 记录 {record_index+1}: 插入文档记录 folder_id={folder_id_int}, container_id={container_id}")
                        cursor.execute("""
                            INSERT INTO document (directory_id, container_id, user_id, title, doi, publication_date)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (folder_id_int, container_id, user_id, title, doi, publish_date))
                        
                        document_id = cursor.lastrowid
                        print(f"[upload_metadata_files] 记录 {record_index+1}: 文档创建成功, id={document_id}")
                        
                        # 处理作者信息
                        authors = record.get('authors', [])
                        if isinstance(authors, list) and authors:
                            print(f"[upload_metadata_files] 记录 {record_index+1}: 处理{len(authors)}个作者")
                            
                            sequence_data = record.get('sequence', [])
                            institutions_data = record.get('institutions', [])
                            locations_data = record.get('institution_location', [])
                            email_data = record.get('email', [])
                            
                            for i, author_name in enumerate(authors):
                                if not author_name:
                                    print(f"[upload_metadata_files] 记录 {record_index+1}: 跳过空作者名称")
                                    continue
                                
                                # 获取作者角色和其他信息
                                sequence = sequence_data[i] if i < len(sequence_data) else "additional"
                                institution = institutions_data[i] if i < len(institutions_data) else None
                                location = locations_data[i] if i < len(locations_data) else None
                                email = email_data[i] if i < len(email_data) else None
                                
                                print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: name={author_name}, sequence={sequence}, institution={institution}")
                                
                                # 确保sequence为标准值
                                if sequence not in ["first", "corresponding", "additional", "other"]:
                                    print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: sequence值({sequence})不标准, 使用'additional'")
                                    sequence = "additional"
                                
                                # 查找或创建作者
                                cursor.execute("""
                                    SELECT author_id FROM author
                                    WHERE user_id = %s AND author_name = %s
                                """, (user_id, author_name))
                                
                                author_result = cursor.fetchone()
                                if author_result:
                                    author_id = author_result['author_id']
                                    print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: 找到现有作者 id={author_id}")
                                    # 更新作者邮箱
                                    if email:
                                        cursor.execute("""
                                            UPDATE author SET author_email = %s
                                            WHERE author_id = %s
                                        """, (email, author_id))
                                        print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: 更新作者邮箱")
                                else:
                                    cursor.execute("""
                                        INSERT INTO author (user_id, author_name, author_email)
                                        VALUES (%s, %s, %s)
                                    """, (user_id, author_name, email))
                                    author_id = cursor.lastrowid
                                    print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: 创建新作者 id={author_id}")
                                
                                # 关联作者与文档
                                cursor.execute("""
                                    INSERT INTO document_author (document_id, author_id, sequence)
                                    VALUES (%s, %s, %s)
                                """, (document_id, author_id, sequence))
                                print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: 创建文档-作者关联成功")
                                
                                # 处理机构信息
                                if institution:
                                    cursor.execute("""
                                        SELECT institution_id FROM institution
                                        WHERE user_id = %s AND institution_name = %s
                                    """, (user_id, institution))
                                    
                                    institution_result = cursor.fetchone()
                                    if institution_result:
                                        institution_id = institution_result['institution_id']
                                        print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: 找到现有机构 id={institution_id}")
                                        # 更新机构地址
                                        if location:
                                            cursor.execute("""
                                                UPDATE institution SET institution_location = %s
                                                WHERE institution_id = %s
                                            """, (location, institution_id))
                                            print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: 更新机构地址")
                                    else:
                                        cursor.execute("""
                                            INSERT INTO institution (user_id, institution_name, institution_location)
                                            VALUES (%s, %s, %s)
                                        """, (user_id, institution, location))
                                        institution_id = cursor.lastrowid
                                        print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: 创建新机构 id={institution_id}")
                                    
                                    # 关联作者与机构
                                    cursor.execute("""
                                        DELETE FROM author_institution
                                        WHERE author_id = %s
                                    """, (author_id,))
                                    print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: 清除旧的作者-机构关联")
                                    
                                    # 检查作者-机构关联是否已存在
                                    cursor.execute("""
                                        SELECT * FROM author_institution
                                        WHERE author_id = %s AND institution_id = %s
                                    """, (author_id, institution_id))
                                    
                                    existing_relation = cursor.fetchone()
                                    
                                    if existing_relation:
                                        print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: 作者-机构关联已存在")
                                    else:
                                        cursor.execute("""
                                            INSERT INTO author_institution (author_id, institution_id)
                                            VALUES (%s, %s)
                                        """, (author_id, institution_id))
                                        print(f"[upload_metadata_files] 记录 {record_index+1}, 作者{i+1}: 创建作者-机构关联成功")
                        
                        # 处理关键词
                        keywords = record.get('keywords', [])
                        if isinstance(keywords, list) and keywords:
                            print(f"[upload_metadata_files] 记录 {record_index+1}: 处理{len(keywords)}个关键词")
                            for keyword_idx, keyword in enumerate(keywords):
                                if not keyword:
                                    print(f"[upload_metadata_files] 记录 {record_index+1}: 跳过空关键词")
                                    continue
                                
                                cursor.execute("""
                                    SELECT keyword_id FROM keyword
                                    WHERE user_id = %s AND keyword_name = %s
                                """, (user_id, keyword))
                                
                                keyword_result = cursor.fetchone()
                                if keyword_result:
                                    keyword_id = keyword_result['keyword_id']
                                    print(f"[upload_metadata_files] 记录 {record_index+1}, 关键词{keyword_idx+1}: 找到现有关键词 '{keyword}' id={keyword_id}")
                                else:
                                    cursor.execute("""
                                        INSERT INTO keyword (user_id, keyword_name)
                                        VALUES (%s, %s)
                                    """, (user_id, keyword))
                                    keyword_id = cursor.lastrowid
                                    print(f"[upload_metadata_files] 记录 {record_index+1}, 关键词{keyword_idx+1}: 创建新关键词 '{keyword}' id={keyword_id}")
                                
                                cursor.execute("""
                                    INSERT INTO document_keyword (document_id, keyword_id)
                                    VALUES (%s, %s)
                                """, (document_id, keyword_id))
                                print(f"[upload_metadata_files] 记录 {record_index+1}, 关键词{keyword_idx+1}: 创建文档-关键词关联成功")
                        
                        # 记录导入成功
                        imported_metadata.append({
                            'title': title,
                            'document_id': document_id
                        })
                        records_in_this_file += 1
                        total_records_imported += 1
                        
                        # 提交事务
                        conn.commit()
                        print(f"[upload_metadata_files] 记录 {record_index+1}: 事务已提交")
                        current_app.logger.info(f"[upload_metadata_files] 记录 {record_index+1}: '{title}' 保存成功, document_id={document_id}")
                        
                    except Exception as e:
                        # 事务回滚
                        conn.rollback()
                        failed_records_in_this_file += 1
                        current_app.logger.error(f"[upload_metadata_files] 记录 {record_index+1} 处理失败: {e}")
                        current_app.logger.error(f"[upload_metadata_files] 详细错误: {traceback.format_exc()}")
                
                file_summaries.append({
                    'filename': file_name,
                    'totalRecords': len(metadata_records),
                    'successfulRecords': records_in_this_file,
                    'failedRecords': failed_records_in_this_file
                })
                
                current_app.logger.info(f"[upload_metadata_files] 文件 {file_name} 处理完成: 成功 {records_in_this_file}, 失败 {failed_records_in_this_file}")
                
            except Exception as e:
                current_app.logger.error(f"[upload_metadata_files] 处理文件 {file_name} 时出现未处理的异常: {e}")
                current_app.logger.error(f"[upload_metadata_files] 详细错误: {traceback.format_exc()}")
    
    except Exception as e:
        current_app.logger.error(f"[upload_metadata_files] 批量导入总体失败: {e}")
        current_app.logger.error(f"[upload_metadata_files] 详细错误: {traceback.format_exc()}")
        return jsonify({
            "error": "服务器错误",
            "message": f"批量导入元数据失败: {str(e)}"
        }), 500
    finally:
        close_db()
        print("[upload_metadata_files] 数据库连接已关闭")
    
    if total_records_imported == 0:
        current_app.logger.warning("[upload_metadata_files] 没有成功导入任何元数据记录")
        return jsonify({
            "code": 1,
            "message": "没有成功导入任何元数据记录",
            "data": {
                "importedCount": 0,
                "files": [file.filename for file in uploaded_files],
                "fileSummaries": file_summaries
            }
        }), 400
    
    current_app.logger.info(f"[upload_metadata_files] 成功导入 {total_records_imported} 条元数据记录")
    return jsonify({
        "code": 0,
        "message": f"成功导入 {total_records_imported} 条元数据记录",
        "data": {
            "importedCount": total_records_imported,
            "files": [file.filename for file in uploaded_files],
            "imported": imported_metadata,
            "fileSummaries": file_summaries
        }
    })
