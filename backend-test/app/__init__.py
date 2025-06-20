from flask import Flask, jsonify, make_response
from flask_bcrypt import Bcrypt
from flask_cors import CORS

import os
import logging
import mysql.connector
import sys

from .config import config
from .db import init_app as init_db_app

bcrypt = Bcrypt()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = os.path.abspath(upload_folder)

    # 修改日志配置，确保输出到终端
    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    else:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    app.logger.info(f"Starting app in {config_name} mode.")
    app.logger.info(f"Database: {app.config.get('OB_DATABASE')}")
    app.logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")

    bcrypt.init_app(app)
    
    # 更新CORS配置
    CORS(app, resources={r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }})
    
    init_db_app(app)

    # Register blueprints
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from .papers.routes import papers_bp
    app.register_blueprint(papers_bp, url_prefix='/api/papers')
    
    from .parse.routes import parse_bp
    app.register_blueprint(parse_bp, url_prefix='/api/parse')
    
    from .folders.routes import folders_bp
    app.register_blueprint(folders_bp, url_prefix='/api/folder')
    
    from .documents.routes import documents_bp
    app.register_blueprint(documents_bp, url_prefix='/api/document')
    
    from .user.routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    from .upload.routes import upload_bp
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    
    from .search.routes import search_bp
    app.register_blueprint(search_bp, url_prefix='/api/search')
    
    # 注册作者和机构蓝图
    from .author.routes import author_bp
    app.register_blueprint(author_bp, url_prefix='/api/author')
    
    from .institution.routes import institution_bp
    app.register_blueprint(institution_bp, url_prefix='/api/institution')
    
    # 注册容器蓝图（期刊/会议）
    from .container.routes import container_bp
    app.register_blueprint(container_bp, url_prefix='/api/container')
    
    # 注册参考文献蓝图
    from .references.routes import references_bp
    app.register_blueprint(references_bp, url_prefix='/api/references')
    
    # 注册统计分析蓝图
    from .stats.routes import stats_bp
    app.register_blueprint(stats_bp, url_prefix='/api/stats')

    # 全局 OPTIONS 请求处理器
    @app.route('/<path:path>', methods=['OPTIONS'])
    @app.route('/', methods=['OPTIONS'])
    def handle_global_options_request(*args, **kwargs):
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Max-Age', '3600')  # 缓存预检响应1小时
        response.status_code = 200
        return response

    # Basic root route for health check or API info
    # curl --noproxy "127.0.0.1" http://127.0.0.1:5000/api/health
    @app.route('/api/health')
    def health_check():
        try:
            # db = app.extensions['mysql_db_conn_pool'].get_connection()
            from .db import get_db, close_db
            conn = get_db()
            conn.ping(reconnect=True)
            db_status = "connected"
            close_db()
        except Exception as e:
            app.logger.error(f"Health check DB connection error: {e}")
            db_status = f"error: {e}"
        return jsonify({
            "status": "healthy",
            "message": "Welcome to LitSay API!",
            "database_status": db_status
            })

    # Global error handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({"error": "Bad Request", "message": str(error.description if hasattr(error, 'description') else error)}), 400
        
    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({"error": "Unauthorized", "message": str(error.description if hasattr(error, 'description') else "Authentication is required and has failed or has not yet been provided.")}), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({"error": "Forbidden", "message": str(error.description if hasattr(error, 'description') else "You don't have the permission to access the requested resource.")}), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found", "message": str(error)}), 404

    @app.errorhandler(405) # Method Not Allowed
    def method_not_allowed_error(error):
        return jsonify({"error": "Method Not Allowed", "message": str(error.description if hasattr(error, 'description') else "The method is not allowed for the requested URL.")}), 405
        
    @app.errorhandler(409) # Conflict
    def conflict_error(error):
        return jsonify({"error": "Conflict", "message": str(error.description if hasattr(error, 'description') else "A conflict occurred with the current state of the target resource.")}), 409

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}", exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500
    
    @app.errorhandler(mysql.connector.Error) # Catch DB errors specifically
    def handle_db_error(error):
        app.logger.error(f"Database operation failed: {error}", exc_info=True)
        return jsonify({"error": "Database Error", "message": "A database error occurred."}), 500

    return app