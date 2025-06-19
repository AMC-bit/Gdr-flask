from flask import render_template
from . import create_character_bp

@create_character_bp.route('/create_character')
def create_character():
    return render_template('create_character.html')