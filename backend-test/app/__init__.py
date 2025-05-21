from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS

import os
import logging
import mysql.connector

from .config import config
from .db import init_app as init_db_app
from .utils.helpers import success_response, error_response

bcrypt = Bcrypt()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    app.config['UPLOAD_FOLDER'] = os.path.abspath(upload_folder)

    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)
    app.logger.info(f"Starting app in {config_name} mode.")
    app.logger.info(f"Database: {app.config.get('OB_DATABASE')}")
    app.logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")

    bcrypt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    init_db_app(app)

    # # Register blueprints
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from .papers.routes import papers_bp
    app.register_blueprint(papers_bp, url_prefix='/api/papers')

    # TODO:
    # from .folders.routes import folders_bp
    # app.register_blueprint(folders_bp, url_prefix='/api/folder')

    # from .documents.routes import documents_bp
    # app.register_blueprint(documents_bp, url_prefix='/api/document')

    # from .uploads.routes import uploads_bp
    # app.register_blueprint(uploads_bp, url_prefix='/api/upload')

    # from .search.routes import search_bp
    # app.register_blueprint(search_bp, url_prefix='/api/search')


    # Health Check
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
        return success_response(data={"status": "healthy", "message": "Welcome to LitSay API!", "database_status": db_status})

    # Global error handlers
    @app.errorhandler(400) # Bad Request
    def bad_request_error(error):
        return error_response(message=getattr(error, 'description', "Bad Request"), status_code=400)

    @app.errorhandler(401) # Unauthorized
    def unauthorized_error(error):
        return error_response(message=getattr(error, 'description', "Unauthorized"), status_code=401)

    @app.errorhandler(403) # Forbidden
    def forbidden_error(error):
        return error_response(message=getattr(error, 'description', "Forbidden"), status_code=403)

    @app.errorhandler(404)
    def not_found_error(error):
        return error_response(message=getattr(error, 'description', "Not Found"), status_code=404)

    @app.errorhandler(405) # Method Not Allowed
    def method_not_allowed_error(error):
        return error_response(message=getattr(error, 'description', "Method Not Allowed"), status_code=405)

    @app.errorhandler(409) # Conflict
    def conflict_error(error):
        return error_response(message=getattr(error, 'description', "Conflict"), status_code=409)

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}", exc_info=True)
        return error_response(message="Internal Server Error", status_code=500, error_details=str(error))


    @app.errorhandler(mysql.connector.Error)
    def handle_db_error(error):
        app.logger.error(f"Database operation failed: {error}", exc_info=True)
        return error_response(message="Database Error", status_code=500, error_details=str(error))
    
    # TODO: (maybe)
    # class AIParsingError(Exception):
    #     pass
    
    # @app.errorhandler(AIParsingError)
    # def handle_ai_parsing_error(error):
    #     app.logger.error(f"AI Parsing Error: {error}", exc_info=True)
    #     return error_response(message=str(error), status_code=500)

    return app