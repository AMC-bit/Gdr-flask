from flask import Blueprint
from . import routes
inventory_bp = Blueprint('inventory', __name__, template_folder='templates')
