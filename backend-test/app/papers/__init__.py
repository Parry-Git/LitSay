from flask import Blueprint

papers_bp = Blueprint('papers', __name__)

from . import routes