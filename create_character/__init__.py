from flask import Blueprint
from . import routes
battle = Blueprint('create_character', __name__, template_folder='templates')
