from flask import request, jsonify, current_app, g
from . import references_bp
from app.db import query_db
from app.utils.decorators import login_required
from .formatters import format_reference_gbt7714, format_reference_apa

@references_bp.route('/generate', methods=['GET'])
@login_required
def generate_references():
    """
    生成指定文件夹下的所有文献的参考文献列表
    支持的格式:
    - gbt7714: 中国国家标准GB/T 7714-2015
    - apa: American Psychological Association (APA)
    """
    folder_id = request.args.get('folderId')
    format_type = request.args.get('format', 'gbt7714')
    user_id = g.current_user['user_id']
    
    if not folder_id:
        return jsonify({"error": "Missing folderId parameter", "message": "缺少文件夹ID参数"}), 400
    
    try:
        documents = query_db("""
            SELECT d.document_id, d.title, d.doi, d.publication_date, 
                   c.container_name, c.type as container_type,
                   c.journal_issue, c.conference_location, c.conference_time
            FROM document d
            LEFT JOIN container c ON d.container_id = c.container_id
            WHERE d.directory_id = %s AND d.user_id = %s 
            ORDER BY d.publication_date DESC, d.title
        """, (folder_id, user_id))
        
        if not documents:
            return jsonify({
                "code": 0,
                "message": "没有找到可用于生成参考文献的期刊文献",
                "data": []
            }), 200
        
        # 为每个文档获取作者信息
        formatted_references = []
        for doc in documents:
            # 获取作者信息，按序列排序
            authors = query_db("""
                SELECT a.author_name, da.sequence
                FROM author a
                JOIN document_author da ON a.author_id = da.author_id
                WHERE da.document_id = %s
                ORDER BY 
                    CASE 
                        WHEN da.sequence = 'first' THEN 1
                        WHEN da.sequence = 'corresponding' THEN 2
                        ELSE 3
                    END
            """, (doc['document_id'],))
            
            
            # 使用选定的格式对参考文献进行格式化
            if format_type == 'gbt7714':
                formatted_ref = format_reference_gbt7714(doc, authors)
            elif format_type == 'apa':
                formatted_ref = format_reference_apa(doc, authors)
            else:
                formatted_ref = f"{doc['title']} (格式 {format_type} 不支持)"
            
            if formatted_ref:
                formatted_references.append(formatted_ref)
        
        return jsonify({
            "code": 0,
            "message": "参考文献生成成功",
            "data": formatted_references
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"生成参考文献出错: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Server Error", 
            "message": f"生成参考文献时发生错误: {str(e)}"
        }), 500

@references_bp.route('/formats', methods=['GET'])
@login_required
def get_supported_formats():
    """获取支持的参考文献格式列表"""
    formats = [
        {
            'value': 'gbt7714',
            'label': 'China National Standard GB/T 7714-2015',
            'description': '中国国家标准，适用于中文学术论文'
        },
        {
            'value': 'apa',
            'label': 'American Psychological Association (APA)',
            'description': '美国心理学会格式，适用于英文学术论文'
        }
    ]
    
    return jsonify({
        "code": 0,
        "message": "获取成功",
        "data": formats
    }), 200
