from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import logging
import mysql.connector

from .config import config
from .db import init_app as init_db_app

# Extensions (can be initialized here or within create_app)
bcrypt = Bcrypt()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configure logging
    if not app.debug and not app.testing:
        # In production, you might want more sophisticated logging
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)
    
    app.logger.info(f"Starting app in {config_name} mode.")
    app.logger.info(f"Database: {app.config.get('OB_DATABASE')}")


    # Initialize extensions
    bcrypt.init_app(app)
    CORS(app) # Enable CORS for all routes, or configure more specifically

    # Initialize database
    init_db_app(app)

    # Register blueprints
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from .papers.routes import papers_bp
    app.register_blueprint(papers_bp, url_prefix='/api/papers')

    # Basic root route for health check or API info
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "healthy", "message": "Welcome to Literature Management API!"})

    # Global error handlers (optional but good practice)
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found", "message": str(error)}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}", exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500
    
    @app.errorhandler(mysql.connector.Error) # Catch DB errors specifically
    def handle_db_error(error):
        app.logger.error(f"Database operation failed: {error}", exc_info=True)
        # Make sure to rollback if an uncommitted transaction exists, though query_db should handle it.
        # from .db import get_db
        # try:
        #     db_conn = get_db()
        #     if db_conn and db_conn.in_transaction: # Check if mysql.connector supports in_transaction
        #         db_conn.rollback()
        # except Exception as e:
        #     app.logger.error(f"Error during rollback attempt: {e}")
        return jsonify({"error": "Database Error", "message": "A database error occurred."}), 500


    return app