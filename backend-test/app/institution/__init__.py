from flask import Blueprint

institution_bp = Blueprint('institution', __name__)

from . import routes
