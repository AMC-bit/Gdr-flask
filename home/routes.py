from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import current_user
from . import home_bp
import os
import json
from config import DATA_DIR_SAVE, DATA_DIR_PGS
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
gioco = Blueprint('gioco', __name__, template_folder=template_dir)

# Home / menu principale
@home_bp.route('/')
def index():
    if current_user.is_authenticated:
        has_personaggi = False
        has_missioni = False
        # controlla se ci sono personaggi e missioni nel file json
        for filename in os.listdir(DATA_DIR_PGS):
                if filename.endswith('.json'):
                    full_path = os.path.join(DATA_DIR_PGS, filename)
                    with open(full_path, 'r') as file:
                        personaggi = json.load(file)
                        for char_id in current_user.character_ids:
                            if personaggi['id'] == char_id:
                                has_personaggi = True
                                break
        file_path_save = os.path.join(DATA_DIR_SAVE, "salvataggio.json")
        if os.path.exists(file_path_save):
            with open(file_path_save) as file:
                salvataggio = json.load(file)
                if 'missione' in salvataggio:
                    has_missioni = True
            can_select_char = has_personaggi and has_missioni #and has_missione
            return render_template('menu.html', can_select_char=can_select_char, has_missioni=has_missioni)
    return render_template('menu.html')

@home_bp.route('/clear')
def clear():
    session.clear()
    return redirect(url_for('home.index'))