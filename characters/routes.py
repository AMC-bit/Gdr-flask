from flask import render_template
from . import characters_bp

@characters_bp.route('/create_char')
def create_char():
    return render_template('create_char.html')
@characters_bp.route('/view_characters')
def view_characters():    
    return render_template('view_characters.html')