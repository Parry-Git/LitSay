from flask import Blueprint, request, jsonify
from database.operations import PaperOperations

# 创建蓝图(Blueprint)对象，用于模块化路由
paper_bp = Blueprint('paper', __name__)

@paper_bp.route('/papers', methods=['GET'])
def get_papers():
    # 获取文献列表
    papers = PaperOperations.get_all()
    return jsonify([p.to_dict() for p in papers])

@paper_bp.route('/papers/<int:paper_id>', methods=['GET'])
def get_paper(paper_id):
    # 获取单个文献详情
    paper = PaperOperations.get_by_id(paper_id)
    return jsonify(paper.to_dict())

@paper_bp.route('/papers/search', methods=['GET'])
def search_papers():
    # 搜索文献
    query = request.args.get('q')
    papers = PaperOperations.search_title(query)
    return jsonify([p.to_dict() for p in papers])

@paper_bp.route('/papers', methods=['POST'])
def add_paper():
    # 添加新文献
    data = request.json
    paper = PaperOperations.create(data)
    return jsonify(paper.to_dict()), 201