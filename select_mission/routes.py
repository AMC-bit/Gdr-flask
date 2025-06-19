from . import select_mission_bp
from flask import render_template

@select_mission_bp.route('/select_mission')
def select_mission():
    return render_template('select_mission.html')