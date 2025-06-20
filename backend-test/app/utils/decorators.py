from functools import wraps
from flask import request, jsonify, current_app, g
import jwt
from app.db import query_db

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1] # Bearer <token>
            except IndexError:
                return jsonify({"error": "Authentication Error", 'message': 'Bearer Token is missing!'}), 401

        if not token:
            return jsonify({"error": "Authentication Error", 'message': 'Authorization is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=current_app.config['JWT_ALGORITHM'])
            user = query_db("SELECT user_id, user_name, role FROM user WHERE user_id = %s", (data['user_id'],), one=True)
            if not user:
                return jsonify({"error": "Authentication Error", "message": "User not found."}), 401
            g.current_user = user

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Authentication Error", 'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Authentication Error", 'message': 'Token is invalid!'}), 401
        except Exception as e:
            current_app.logger.error(f"Token validation error: {e}")
            return jsonify({"error": "Authentication Error", 'message': 'Token validation failed!'}), 401

        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """检查用户是否为管理员的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 确保用户已登录
        if not hasattr(g, 'current_user'):
            return jsonify({
                "error": "Authentication Error", 
                "message": "未认证，请先登录"
            }), 401
        
        # 检查用户角色
        if g.current_user['role'] != 1:  # 1表示管理员
            return jsonify({
                "error": "Permission Denied", 
                "message": "需要管理员权限"
            }), 403
        
        return f(*args, **kwargs)
    return decorated
