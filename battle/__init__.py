from flask import Blueprint
from . import routes
battle = Blueprint('battle', __name__, template_folder='templates')
