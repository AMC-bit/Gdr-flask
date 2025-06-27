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
    has_missione = 'missione' in session
    can_select_char = has_personaggi and has_ambiente and has_missione
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


@gioco.route('/test-inventory', methods=['GET', 'POST'])
def test_inventory():
    # Dati di esempio per testare la pagina
    pg_nome = "Gandalf"
    oggetti = [
        {"nome": "Pozione di Guarigione"},
        {"nome": "Pergamena Magica"},
        {"nome": "Antidoto"}
    ]
    oggetto_selezionato = None
    bersagli = []
    messaggio = None

    if request.method == 'POST':
        if 'action' in request.form and request.form['action'] == 'close':
            return redirect(url_for('gioco.index'))

    oggetto = request.form.get('oggetto')
    if oggetto:
        oggetto_selezionato = oggetto
        # Simula bersagli per test
        bersagli = [
            {"nome": "Frodo", "salute": 50, "salute_max": 80, "classe": "Hobbit", "tipologia": "Alleato"},
            {"nome": "Orco", "salute": 30, "salute_max": 60, "classe": "Guerriero", "tipologia": "Nemico"}
        ]

    bersaglio = request.form.get('bersaglio')
    if oggetto and bersaglio:
        messaggio = f"{pg_nome} usa {oggetto} su {bersaglio}! Successo!"

    return render_template(
        'inventory.html',
        pg_nome=pg_nome,
        oggetti=oggetti,
        oggetto_selezionato=oggetto_selezionato,
        bersagli=bersagli,
        messaggio=messaggio)


@gioco.route('/clear')
def clear():
    session.clear()
    return redirect(url_for('gioco.index'))