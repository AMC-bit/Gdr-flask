from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from gioco.oggetto import BombaAcida, Medaglione, Oggetto, PozioneCura
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

    inventario_pg = Inventario(pg_test)
    inventario_pg.oggetti = [
        PozioneCura(),
        Medaglione(),
        BombaAcida()
    ]

    bersagli = [
        pg_test,
        Guerriero("Aragorn"),
        Ladro("Frodo"),
        Mago("Saruman"),
        Guerriero("Orco")
    ]

    oggetto_selezionato = None
    bersaglio_selezionato = None
    messaggio = None

    # Gestione della richiesta POST
    if request.method == 'POST':
        if 'action' in request.form and request.form['action'] == 'close':
            return redirect(url_for('gioco.index'))

    oggetto = request.form.get('oggetto')
    bersaglio = request.form.get('bersaglio')

    if oggetto:
        oggetto_selezionato = next(
            (o for o in inventario_pg.oggetti if o.nome == oggetto), None
        )
        if not oggetto_selezionato:
            flash(f"Oggetto '{oggetto}' non trovato nell'inventario.", 'error')
            return redirect(url_for('inventario.test_inventory'))
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