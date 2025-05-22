from flask import Blueprint

folders_bp = Blueprint('folders', __name__)

from . import routes