from flask import Blueprint
from . import routes
create_character_bp = Blueprint('create_character', __name__, template_folder='templates')
