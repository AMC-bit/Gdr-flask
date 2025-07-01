from flask import Blueprint, render_template, request, session, redirect, url_for, Flask

# Istanze di test
from gioco.personaggio import Personaggio
from gioco.classi import Mago, Guerriero, Ladro
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
gioco = Blueprint('gioco', __name__, template_folder=template_dir)

# Home / menu principale
@gioco.route('/')
def index():
    has_personaggi = 'personaggi' in session
    has_ambiente = 'ambiente' in session
    #has_missione = 'missione' in session
    can_select_char = has_personaggi and has_ambiente #and has_missione
    return render_template('menu.html', can_select_char=can_select_char)


# Mostra i log dello scontro, permette di attaccare e usare l'inventario
@gioco.route('/battle', methods=['GET', 'POST'])
def battle():
    # DA RECUPERARE
    # È il personaggio che sta attualmente giocando il suo turno
    personaggio_attivo =""
    nome_personaggio_attivo = "Genoveffo"

    # Questa variabile booleana disabilita i pulsanti attacca e usa inventario,
    # è da switchare quando è il turno del personaggio
    # DA RECUPERARE
    buttons_diasable = True

    return render_template('battle.html', nome_personaggio_attivo = nome_personaggio_attivo)


@gioco.route('/clear')
def clear():
    session.clear()
    return redirect(url_for('gioco.index'))