from flask import request, jsonify, current_app, g
# from flask_bcrypt import Bcrypt
import jwt
import datetime

from . import auth_bp
from app.db import query_db
from app.utils.decorators import login_required
from app.utils.helpers import success_response, error_response
from app import bcrypt


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Validation Error", "message": "Username and password are required."}), 400
    username = data['username']
    password = data['password']

    existing_user = query_db("SELECT * FROM user WHERE user_name = %s", (username,), one=True)
    if existing_user:
        return jsonify({"error": "Conflict", "message": "Username already exists."}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        query_db("INSERT INTO user (user_name, password_hash) VALUES (%s, %s)",
                 (username, hashed_password), commit=True)
        return success_response(data={"userId": user_id}, message="Registered successfully.", status_code=201)
    except Exception as e:
        current_app.logger.error(f"Registration error: {e}")
        return error_response(message="Could not register user.", status_code=500, error_details=e)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return error_response(message="Username and password are required.", status_code=400)

    username = data['username']
    password = data['password']
    user = query_db("SELECT user_id, user_name, password_hash, role FROM user WHERE user_name = %s", (username,), one=True)

    if user and bcrypt.check_password_hash(user['password_hash'], password):
        token_payload = {
            'user_id': user['user_id'],
            'username': user['user_name'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=current_app.config['JWT_EXPIRATION_DELTA_SECONDS'])
        }
        token = jwt.encode(token_payload, current_app.config['JWT_SECRET_KEY'], algorithm=current_app.config['JWT_ALGORITHM'])
        user_info = {"id": user['user_id'], "username": user['user_name'], "role": user['role']}
        return success_response(data={"user": user_info, "token": token}, message="Login successful.")
    else:
        return error_response(message="Invalid username or password.", status_code=401)

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    # For JWT, logout is primarily handled by the client deleting the token.
    return success_response(message="Logout successful.")

@auth_bp.route('/current', methods=['GET'])
@login_required
def current_user_info():
    # g.current_user is set by @login_required
    user_data = {
        "id": g.current_user['user_id'],
        "username": g.current_user['user_name'],
        "role": g.current_user['role']
    }
    return success_response(data=user_data, message="Get user info successfully.")

@auth_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    user_id = g.current_user['user_id']
    try:
        total_documents = query_db("SELECT COUNT(*) as count FROM document WHERE user_id = %s", (user_id,), one=True)['count']
        total_folders = query_db("SELECT COUNT(*) as count FROM directory WHERE user_id = %s", (user_id,), one=True)['count']
        # storage_used_mb = query_db("SELECT SUM(filesize_in_mb) FROM document_files WHERE user_id = %s", (user_id,), one=True)['sum']

        stats = {
            "totalDocuments": total_documents,
            "totalFolders": total_folders,
            # "storageUsedMb": storage_used_mb or 0,
            "tagsCount": query_db("SELECT COUNT(DISTINCT keyword_id) as count FROM keyword WHERE user_id = %s", (user_id,), one=True)['count']
        }
        return success_response(data=stats, message="Get user stats successfully.")
    except Exception as e:
        current_app.logger.error(f"Error getting user stats: {e}", exc_info=True)
        return error_response(message="Failed to retrieve user statistics.", status_code=500, error_details=e)

