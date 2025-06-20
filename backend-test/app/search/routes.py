from flask import request, jsonify, current_app, g, make_response
from . import search_bp
from app.db import query_db
from app.utils.decorators import login_required
import jwt

@search_bp.route('/', methods=['GET'])
def search_library():
    """搜索库中的文档、作者和机构"""
    # 支持从URL参数获取token
    token = request.args.get('token')
    
    # 如果提供了token，尝试解码获取用户ID
    user_id = None
    if token:
        try:
            payload = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'],
                algorithms=[current_app.config.get('JWT_ALGORITHM', 'HS256')]
            )
            user_id = payload.get('user_id')
        except jwt.PyJWTError as e:
            current_app.logger.error(f"Token解析失败: {e}")
            return jsonify({
                "error": "认证失败", 
                "message": "无效的认证令牌"
            }), 401
    
    # 如果无法获取用户ID
    if not user_id:
        return jsonify({
            "error": "认证失败", 
            "message": "请提供有效的认证信息"
        }), 401
    
    # 获取基本搜索参数
    query = request.args.get('q', '')
    print(f"传入参数：{request.args}")
    
    # 获取高级搜索参数 - 修正使用getlist()获取数组参数
    use_regex = request.args.get('regex') == '1'
    search_fields = request.args.get('fields', '').split(',') if request.args.get('fields') else []
    date_from = request.args.get('dateFrom', '')
    date_to = request.args.get('dateTo', '')
    
    # 修正获取数组参数的方式
    keywords_and = request.args.getlist('keywordsAnd[]')
    if not keywords_and and request.args.get('keywordsAnd'):  # 兼容非数组方式
        keywords_and = request.args.get('keywordsAnd', '').split(',')
    
    keywords_or = request.args.getlist('keywordsOr[]')
    if not keywords_or and request.args.get('keywordsOr'):  # 兼容非数组方式
        keywords_or = request.args.get('keywordsOr', '').split(',')
    
    document_type = request.args.get('type', '')
    
    print(f"高级搜索参数: query={query}, use_regex={use_regex}, search_fields={search_fields}, " 
          f"date_from={date_from}, date_to={date_to}, keywords_and={keywords_and}, keywords_or={keywords_or}, "
          f"document_type={document_type}")
    
    # 验证搜索参数，修改为允许高级搜索时不提供查询内容
    has_advanced_filters = keywords_and or keywords_or or date_from or date_to or document_type
    if not use_regex and (not query or len(query) < 1) and not has_advanced_filters:
        return jsonify({
            "code": 1,
            "message": "搜索词太短或未提供任何搜索条件",
            "data": {"results": []}
        }), 400
    
    # 准备搜索条件
    search_term = query
    results = []
    
    try:
        # 构建SQL查询条件
        document_conditions = []
        document_params = []
        
        # 基本的文档查询条件 - 只有当search_term不为空时才添加
        if use_regex:
            # 正则表达式搜索
            try:
                # 在MySQL中使用REGEXP进行正则搜索
                if search_term:  # 修改：只有当search_term不为空时才添加条件
                    title_doi_conditions = []
                    if not search_fields or 'title' in search_fields:
                        title_doi_conditions.append("d.title REGEXP %s")
                        document_params.append(search_term)
                        print(f"添加标题正则条件: d.title REGEXP {search_term}")
                    if not search_fields or 'doi' in search_fields:
                        title_doi_conditions.append("d.doi REGEXP %s")
                        document_params.append(search_term)
                        print(f"添加DOI正则条件: d.doi REGEXP {search_term}")
                    
                    # 将标题和DOI条件合并为一个OR条件组
                    if title_doi_conditions:
                        document_conditions.append(f"({' OR '.join(title_doi_conditions)})")
                        print(f"正则表达式搜索条件: {' OR '.join(title_doi_conditions)}")
                
            except Exception as e:
                print(f"正则表达式错误: {e}")
                return jsonify({
                    "code": 1,
                    "message": f"正则表达式错误: {str(e)}",
                    "data": {"results": []}
                }), 400
        else:
            # 普通搜索，使用LIKE
            if search_term:  # 修改：只有当search_term不为空时才添加条件
                search_pattern = f"%{search_term}%"
                title_doi_conditions = []
                
                if not search_fields or 'title' in search_fields:
                    title_doi_conditions.append("d.title LIKE %s")
                    document_params.append(search_pattern)
                    print(f"添加标题条件: d.title LIKE {search_pattern}")
                if not search_fields or 'doi' in search_fields:
                    title_doi_conditions.append("d.doi LIKE %s")
                    document_params.append(search_pattern)
                    print(f"添加DOI条件: d.doi LIKE {search_pattern}")
                
                # 将标题和DOI条件合并为一个OR条件组
                if title_doi_conditions:
                    document_conditions.append(f"({' OR '.join(title_doi_conditions)})")
                    print(f"普通搜索条件: {' OR '.join(title_doi_conditions)}")
        
        # 日期范围过滤
        if date_from:
            document_conditions.append("d.publication_date >= %s")
            document_params.append(date_from)
            print(f"添加日期起始条件: d.publication_date >= {date_from}")
        if date_to:
            document_conditions.append("d.publication_date <= %s")
            document_params.append(date_to)
            print(f"添加日期结束条件: d.publication_date <= {date_to}")
        
        # 关键词过滤 (AND) - 确保文档包含所有指定关键词
        if keywords_and:
            # 为每个关键词创建EXISTS子查询，并用AND连接
            and_conditions = []
            and_params = []
            
            for keyword in keywords_and:
                if keyword.strip():
                    and_conditions.append("""
                        EXISTS (
                            SELECT 1 FROM document_keyword dk
                            JOIN keyword k ON dk.keyword_id = k.keyword_id
                            WHERE dk.document_id = d.document_id 
                            AND k.keyword_name LIKE %s 
                            AND k.user_id = %s
                        )
                    """)
                    and_params.append(f"%{keyword.strip()}%")
                    and_params.append(user_id)
                    print(f"添加AND关键词条件: {keyword.strip()}")
            
            if and_conditions:
                # 用AND连接所有条件，要求文档必须满足每一个关键词条件
                document_conditions.append(f"({' AND '.join(and_conditions)})")
                document_params.extend(and_params)
                print(f"添加AND关键词组合条件: {' AND '.join(and_conditions)}")
        
        # 关键词过滤 (OR) - 只要文档包含任一指定关键词即可
        if keywords_or:
            # 为每个关键词创建EXISTS子查询，并用OR连接
            or_conditions = []
            or_params = []
            
            for keyword in keywords_or:
                if keyword.strip():
                    or_conditions.append("""
                        EXISTS (
                            SELECT 1 FROM document_keyword dk
                            JOIN keyword k ON dk.keyword_id = k.keyword_id
                            WHERE dk.document_id = d.document_id 
                            AND k.keyword_name LIKE %s
                            AND k.user_id = %s
                        )
                    """)
                    or_params.append(f"%{keyword.strip()}%")
                    or_params.append(user_id)
                    print(f"添加OR关键词条件: {keyword.strip()}")
            
            if or_conditions:
                # 用OR连接所有条件，文档只需要满足任一关键词条件
                document_conditions.append(f"({' OR '.join(or_conditions)})")
                document_params.extend(or_params)
                print(f"添加OR关键词组合条件: {' OR '.join(or_conditions)}")
        
        # 文档类型过滤
        if document_type:
            if document_type == 'journal':
                document_conditions.append("c.type = 'journal'")
                print("添加journal类型条件")
            elif document_type == 'conference':
                document_conditions.append("c.type = 'conference'")
                print("添加conference类型条件")
            elif document_type == 'paper':
                document_conditions.append("c.type IS NULL")  # 假设没有容器类型的是普通论文
                print("添加paper类型条件")
        
        # 用户ID条件 (必须)
        document_conditions.append("d.user_id = %s")
        document_params.append(user_id)
        print(f"添加用户ID条件: d.user_id = {user_id}")
        
        # 构建最终的文档查询
        if document_conditions:
            # 修正where_clause构建逻辑，确保使用AND连接条件
            where_clause = " AND ".join(document_conditions)
            
            # 构建完整SQL查询
            document_query = f"""
                SELECT d.document_id as id, d.title as name, 'document' as type,
                       CASE 
                           WHEN d.doi = %s THEN 'doi'
                           WHEN d.doi LIKE %s THEN 'doi'
                           ELSE 'title'
                       END as matchField,
                       dir.directory_name as path, d.doi
                FROM document d
                JOIN directory dir ON d.directory_id = dir.directory_id
                LEFT JOIN container c ON d.container_id = c.container_id
                WHERE {where_clause}
                ORDER BY CASE 
                    WHEN d.doi = %s THEN 0
                    WHEN d.title = %s THEN 1
                    WHEN d.title LIKE %s THEN 2
                    WHEN d.doi LIKE %s THEN 3
                    ELSE 4
                END
                LIMIT 20
            """
            
            # 添加排序需要的参数
            final_params = [query or '', f"%{query or ''}%"] + document_params + [query or '', query or '', f"{query or ''}%", f"%{query or ''}%"]
            
            print(f"文档查询SQL: {document_query}")
            print(f"文档查询参数: {final_params}")
            
            # 执行查询
            try:
                documents = query_db(document_query, final_params)
                print(f"查询到文档数量: {len(documents) if documents else 0}")
                print(f"文档查询结果: {documents[:2]}")  # 只打印前两条结果，避免日志过大
            except Exception as e:
                print(f"文档查询执行错误: {e}")
                documents = []
            
            # 格式化文档路径和详细信息
            for doc in documents:
                if 'path' in doc and doc['path']:
                    doc['path'] = f"位于 {doc['path']}"
                
                if 'matchField' in doc and doc['matchField'] == 'doi' and 'doi' in doc and doc['doi']:
                    doc['match'] = f"匹配DOI: {doc['doi']}"
                
                results.append(doc)
        
        # 只有当不是高级搜索时才搜索作者和机构
        has_advanced_filters = keywords_and or keywords_or or date_from or date_to or document_type
        
        if query and not has_advanced_filters:
            # 作者搜索
            if not search_fields or 'author' in search_fields:
                authors_query = """
                    SELECT DISTINCT a.author_id as id, a.author_name as name, 'author' as type, 'author' as matchField
                    FROM author a
                    WHERE a.user_id = %s AND a.author_name LIKE %s
                    LIMIT 3
                """
                print(f"作者查询SQL: {authors_query}")
                print(f"作者查询参数: [{user_id}, %{query}%]")
                
                try:
                    authors = query_db(authors_query, (user_id, f"%{query}%"))
                    print(f"查询到作者数量: {len(authors) if authors else 0}")
                    results.extend(authors)
                except Exception as e:
                    print(f"作者查询执行错误: {e}")
            
            # 机构搜索
            if not search_fields or 'affiliation' in search_fields:
                institutions_query = """
                    SELECT DISTINCT i.institution_id as id, i.institution_name as name, 'institution' as type, 
                           'affiliation' as matchField, i.institution_location as location
                    FROM institution i
                    WHERE i.user_id = %s AND i.institution_name LIKE %s
                    LIMIT 3
                """
                print(f"机构查询SQL: {institutions_query}")
                print(f"机构查询参数: [{user_id}, %{query}%]")
                
                try:
                    institutions = query_db(institutions_query, (user_id, f"%{query}%"))
                    print(f"查询到机构数量: {len(institutions) if institutions else 0}")
                    
                    for inst in institutions:
                        if 'location' in inst and inst['location']:
                            inst['path'] = inst['location']
                            del inst['location']
                        results.append(inst)
                except Exception as e:
                    print(f"机构查询执行错误: {e}")

        # 输出最终结果数量
        print(f"最终搜索结果总数: {len(results)}")
        print(f"结果分类: 文档: {sum(1 for r in results if r.get('type') == 'document')}, "
              f"作者: {sum(1 for r in results if r.get('type') == 'author')}, "
              f"机构: {sum(1 for r in results if r.get('type') == 'institution')}")

        return jsonify({
            "code": 0,
            "message": "搜索成功",
            "data": {
                "query": query,
                "results": results
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"搜索失败: {e}")
        print(f"搜索出错: {e}")
        return jsonify({
            "error": "服务器错误", 
            "message": f"搜索失败: {str(e)}"
        }), 500
