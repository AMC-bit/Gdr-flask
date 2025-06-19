from flask import render_template
from . import battle_bp

@battle_bp.route('/battle')
def battle():
    return render_template('battle.html')