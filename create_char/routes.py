from flask import render_template
from . import create_char_bp

@create_char_bp.route('/create_char')
def create_char():
    return render_template('create_char.html')