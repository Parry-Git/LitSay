from flask import Blueprint

search_bp = Blueprint('search', __name__)

from . import routes

@search_bp.route('/', methods=['OPTIONS'])
def handle_options():
    response = current_app.make_default_options_response()
    headers = response.headers
    # Add CORS headers here
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
