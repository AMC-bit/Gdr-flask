from flask import Blueprint, render_template, request, session, redirect, url_for, Flask
from flask_login import current_user
# Istanze di test
from gioco.personaggio import Personaggio
from gioco.classi import Mago, Guerriero, Ladro
import os
import json
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
gioco = Blueprint('gioco', __name__, template_folder=template_dir)

# Home / menu principale
@gioco.route('/')
def index():
    if current_user.is_authenticated:
        has_personaggi = False
        has_missioni = False
        # controlla se ci sono personaggi e missioni nel file json
        file_path = os.path.join('data', 'json', 'personaggi')
        for filename in os.listdir(file_path):
                print("TEST1", filename)
                if filename.endswith('.json'):
                    full_path = os.path.join(file_path, filename)
                    with open(full_path, 'r') as file:
                        personaggi = json.load(file)
                        for char_id in current_user.character_ids:
                            print("TEST2", char_id)
                            print("TEST3",personaggi['id'])
                            if personaggi['id'] == char_id:
                                has_personaggi = True
                                break
        has_missioni = 'missione' in session
        if has_missioni:
            print(has_personaggi)
        can_select_char = has_personaggi and has_missioni #and has_missione
        return render_template('menu.html', can_select_char=can_select_char, has_missioni=has_missioni)
    return render_template('menu.html')

@gioco.route('/clear')
def clear():
    session.clear()
    return redirect(url_for('gioco.index'))