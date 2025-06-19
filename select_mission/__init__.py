from flask import Blueprint
from . import routes
select_mission_bp = Blueprint('select_mission', __name__, template_folder='templates')
