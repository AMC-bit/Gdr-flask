from flask import Blueprint
from . import routes
battle = Blueprint('view_characters', __name__, template_folder='templates')
