from functools import wraps
from flask import request, jsonify, current_app, g
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1] # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Bearer token malformed!'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            # You can fetch the user from DB here if needed and pass to g.current_user
            # For simplicity, we'll just pass the user_id from token
            g.current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            current_app.logger.error(f"Token validation error: {e}")
            return jsonify({'message': 'Token validation failed!'}), 401

        return f(*args, **kwargs)
    return decorated