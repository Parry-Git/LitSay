from flask import request, jsonify, current_app, g
from . import stats_bp
from app.db import query_db
from app.utils.decorators import login_required


@stats_bp.route('/overview', methods=['GET'])
@login_required
def get_stats_overview():
    """
    获取用户统计概览数据:
    - 文献总数
    - 文件夹数量
    - 作者数量
    """
    user_id = g.current_user['user_id']
    
    try:
        # 1. 获取用户保存的文献数量
        documents_count = query_db("""
            SELECT COUNT(*) as count
            FROM document
            WHERE user_id = %s
        """, (user_id,), one=True)['count']
        
        # 2. 获取用户创建的文件夹数量
        folders_count = query_db("""
            SELECT COUNT(*) as count
            FROM directory
            WHERE user_id = %s
        """, (user_id,), one=True)['count']
        
        # 3. 获取用户收录的作者数量 (通过document_author关联表)
        authors_count = query_db("""
            SELECT COUNT(DISTINCT da.author_id) as count
            FROM document_author da
            JOIN document d ON da.document_id = d.document_id
            WHERE d.user_id = %s
        """, (user_id,), one=True)['count']
        
        # print(f"获取统计概览: 文献数量={documents_count}, 文件夹数量={folders_count}, 作者数量={authors_count}")
        
        return jsonify({
            "code": 0,
            "message": "获取统计概览成功",
            "data": {
                "documentsCount": documents_count,
                "foldersCount": folders_count,
                "authorsCount": authors_count
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取统计概览失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500,
            "error": "Server Error",
            "message": f"获取统计概览失败: {str(e)}"
        }), 500


@stats_bp.route('/keywords/top', methods=['GET'])
@login_required
def get_keywords_top5():
    """
    获取关键词TOP5统计:
    - 横坐标是关键字
    - 纵坐标是包含该关键字的文献数量
    """
    user_id = g.current_user['user_id']
    
    try:
        # 查询用户的TOP5关键词
        keywords_top = query_db("""
            SELECT k.keyword_name as keyword, COUNT(dk.document_id) as count
            FROM keyword k
            JOIN document_keyword dk ON k.keyword_id = dk.keyword_id
            JOIN document d ON dk.document_id = d.document_id
            WHERE d.user_id = %s
            GROUP BY k.keyword_id, k.keyword_name
            ORDER BY count DESC
            LIMIT 5
        """, (user_id,))
        
        # print(f"获取关键词TOP5: {keywords_top}")
        
        # 如果没有数据，返回空列表
        if not keywords_top:
            keywords_top = []
            
        return jsonify({
            "code": 0,
            "message": "获取关键词TOP5成功",
            "data": keywords_top
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取关键词TOP5失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500,
            "error": "Server Error",
            "message": f"获取关键词TOP5失败: {str(e)}"
        }), 500


@stats_bp.route('/authors/stars', methods=['GET'])
@login_required
def get_authors_top5():
    """
    获取作者星级TOP5统计:
    - 横坐标是作者
    - 纵坐标是该用户对应的该作者所有文献的star数之和
    
    注意: 如果数据库中没有真实的star字段,我们使用基于文档数量的模拟数据
    """
    user_id = g.current_user['user_id']
    
    try:
        # 首先尝试查询是否存在stars字段
        try:
            author_stars = query_db("""
                SELECT a.author_name as author, SUM(d.stars) as stars
                FROM author a
                JOIN document_author da ON a.author_id = da.author_id
                JOIN document d ON da.document_id = d.document_id
                WHERE d.user_id = %s
                GROUP BY a.author_id, a.author_name
                ORDER BY stars DESC
                LIMIT 5
            """, (user_id,))
            
            # print(f"获取作者星级TOP5: {author_stars}")
            
            # 如果查询结果为空或stars全为0,则改用模拟数据
            if not author_stars or all(author['stars'] == 0 for author in author_stars):
                raise Exception("No stars data found")
                
        except Exception:
            # 回退策略: 使用作者的文档数量作为模拟的"星级"指标
            current_app.logger.info("使用文档数量作为星级模拟数据")
            author_stars = query_db("""
                SELECT a.author_name as author, COUNT(da.document_id) * 5 as stars
                FROM author a
                JOIN document_author da ON a.author_id = da.author_id
                JOIN document d ON da.document_id = d.document_id
                WHERE d.user_id = %s
                GROUP BY a.author_id, a.author_name
                ORDER BY stars DESC
                LIMIT 5
            """, (user_id,))
        
        # 如果还是没有数据,返回空列表
        if not author_stars:
            author_stars = []
            
        return jsonify({
            "code": 0,
            "message": "获取作者星级TOP5成功",
            "data": author_stars
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取作者星级TOP5失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500, 
            "error": "Server Error",
            "message": f"获取作者星级TOP5失败: {str(e)}"
        }), 500
