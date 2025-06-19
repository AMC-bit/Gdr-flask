from flask import Blueprint
from . import routes
view_characters_bp = Blueprint('view_characters', __name__, template_folder='templates')
