from flask import Blueprint

author_bp = Blueprint('author', __name__)

from . import routes
