from flask import Blueprint
from . import routes
select_environment_bp = Blueprint('select_environment', __name__, template_folder='templates')
