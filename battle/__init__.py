from flask import Blueprint
from . import routes
battle_bp = Blueprint('battle', __name__, template_folder='templates')
