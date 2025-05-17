from flask import request, jsonify, current_app, g
from . import auth_bp
from app import bcrypt # from app's __init__
from app.db import query_db # Use our query helper
from app.utils.decorators import token_required
import jwt
import datetime

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'message': 'Missing username, password or email'}), 400

    username = data['username']
    email = data['email']
    # Check if user already exists
    user_by_username = query_db("SELECT * FROM users WHERE username = %s", (username,), one=True)
    if user_by_username:
        return jsonify({'message': 'Username already exists'}), 409 # Conflict
    
    user_by_email = query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)
    if user_by_email:
        return jsonify({'message': 'Email already registered'}), 409

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    try:
        query_db("INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
                 (username, hashed_password, email), commit=True)
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        current_app.logger.error(f"Registration failed: {e}")
        return jsonify({'message': 'Registration failed due to server error'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400

    username = data['username']
    password = data['password']

    user = query_db("SELECT * FROM users WHERE username = %s", (username,), one=True)

    if not user or not bcrypt.check_password_hash(user['password_hash'], password):
        return jsonify({'message': 'Invalid username or password'}), 401

    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24) # Token expires in 24 hours
    }, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token, 'user': {'id': user['id'], 'username': user['username']}}), 200

@auth_bp.route('/me', methods=['GET'])
@token_required # This route now requires a valid token
def get_current_user():
    # g.current_user_id is set by @token_required decorator
    user = query_db("SELECT id, username, email FROM users WHERE id = %s", (g.current_user_id,), one=True)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user), 200