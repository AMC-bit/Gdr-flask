from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from gioco.oggetto import Oggetto
from gioco.personaggio import Personaggio
from gioco.classi import Ladro, Mago, Guerriero
from .inventario import Inventario

inventario_bp = Blueprint(
    'inventario', __name__, template_folder='../templates'
)

@inventario_bp.route('/test-inventory', methods=['GET', 'POST'])
def test_inventory():
    # Dati di esempio per testare la pagina

    pg_nome = "Gandalf"
    pg_test = Mago(pg_nome)
    session['pg'] = pg_test.to_dict()  # Salva il personaggio nella session
    session.modified = True  # Assicurati che la session sia aggiornata
    if 'pg' not in session:
        flash("Personaggio non trovato nella sessione.", "error")
    else:
        pg_nome = session['pg']['nome']

    inventario_pg = Inventario.from_dict(session.get('inventario', {}))
    inventario_pg.oggetti = [
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
        oggetti=inventario_pg.mostra_lista_inventario(),
        oggetto_selezionato=oggetto_selezionato,
        bersagli=bersagli,
        messaggio=messaggio
    )