from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import current_user
from . import home_bp
import os
import json
from config import DATA_DIR_SAVE, DATA_DIR_PGS, load_leaderboard
template_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'templates')
    )
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
                try:
                    with open(full_path, 'r', encoding='utf-8') as file:
                        personaggi = json.load(file)
                        for char_id in current_user.character_ids:
                            if personaggi['id'] == char_id:
                                has_personaggi = True
                                break
                except (json.JSONDecodeError, KeyError, IOError) as e:
                    # Salta i file JSON corrotti o malformati
                    print(f"Errore nel caricamento del file {filename}: {e}")
                    continue
        file_path_save = os.path.join(DATA_DIR_SAVE, "salvataggio.json")
        if os.path.exists(file_path_save):
            try:
                with open(file_path_save, 'r', encoding='utf-8') as file:
                    salvataggio = json.load(file)
                    if 'missione' in salvataggio:
                        has_missioni = True
            except (json.JSONDecodeError, IOError) as e:
                # Gestisce errori nel file di salvataggio
                print(f"Errore nel caricamento del file di salvataggio: {e}")
                has_missioni = False

            users_stats = load_leaderboard()
            # utilizzo di 'sorted'
            # - un elemento iterabile ad esempio 'content.items'
            # - con 'content.items' ottengo una lista di tuple dal dizionario
            # - 'key=lambda x: x[1]['punteggio']' vuol dire per ogni
            # elemento x, prendi il punteggio corrispondente
            users_stats_sorted = sorted(users_stats.items(), key=lambda x: x[1]['punteggio'], reverse=True)

            can_select_char = has_personaggi and has_missioni
            return render_template(
                'menu.html',
                can_select_char=can_select_char,
                has_missioni=has_missioni,
                users_stats=load_leaderboard()
                )

    return render_template('menu.html', users_stats_sorted=users_stats_sorted)


@home_bp.route('/clear')
def clear():
    session.clear()
    return redirect(url_for('home.index'))