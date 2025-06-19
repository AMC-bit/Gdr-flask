from flask import render_template
from . import select_environment_bp

@select_environment_bp.route('/view_characters')
def view_characters():    
    return render_template('view_characters.html')