from flask import render_template
from . import environment_bp

@environment_bp.route('/select_environment')
def select_environment():
    return render_template('select_environment.html')