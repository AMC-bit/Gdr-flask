from flask import render_template
from . import select_environment_bp

@select_environment_bp.route('/select_environment')
def create_character():
    return render_template('select_environment.html')