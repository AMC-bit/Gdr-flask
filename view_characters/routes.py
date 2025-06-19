from flask import render_template
from . import view_characters_bp

@view_characters_bp.route('/view_characters')
def view_characters():    
    return render_template('view_characters.html')