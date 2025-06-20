from flask import Blueprint

references_bp = Blueprint('references', __name__)

from . import routes
