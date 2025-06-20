from flask import Blueprint

stats_bp = Blueprint('stats', __name__)

from . import routes
