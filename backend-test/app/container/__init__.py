from flask import Blueprint

container_bp = Blueprint('container', __name__)

from . import routes
