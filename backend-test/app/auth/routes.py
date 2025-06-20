from flask import request, jsonify, current_app, g
# from flask_bcrypt import Bcrypt
import jwt
import datetime

from . import auth_bp
from app.db import query_db
from app.utils.decorators import login_required
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
        return jsonify({"message": "User registered successfully. Please login."}), 201
    except Exception as e:
        current_app.logger.error(f"Registration error: {e}")
        return jsonify({"error": "Server Error", "message": "Could not register user."}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Validation Error", "message": "Username and password are required."}), 400
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
        return jsonify({"message": "Login successful.", "access_token": token, "user_id": user['user_id'], "username": user['user_name'], "role": user['role']}), 200
    else:
        return jsonify({"error": "Authentication Failed", "message": "Invalid username or password."}), 401

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    # g.current_user is set by the @login_required decorator
    return jsonify({
        "user_id": g.current_user['user_id'],
        "username": g.current_user['user_name'],
        "role": g.current_user['role']
    }), 200

# add refresh token route or logout (client-side token invalidation)