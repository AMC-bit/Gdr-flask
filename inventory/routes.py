from . import inventory_bp
from flask import render_template, request, session, redirect, url_for, flash
from gioco.oggetto import BombaAcida, Medaglione, Oggetto, PozioneCura
from gioco.personaggio import Personaggio
from gioco.classi import Ladro, Mago, Guerriero
from gioco.inventario import Inventario
from utils.messaggi import Messaggi

@inventory_bp.route('/inventory')
def inventory():
    return render_template('inventory.html')

@inventory_bp.route('/test-inventory', methods=['GET', 'POST'])
def test_inventory():
    # Dati di esempio per testare la pagina

    pg_test = Mago("Gandalf")
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
    bersagli_dict = {b.id: b for b in bersagli}

    oggetto_selezionato = request.form.get('oggetto')
    bersaglio_id = request.form.get('bersaglio')
    messaggio = None

    # Gestione della richiesta POST
    if request.method == 'POST':
        if 'action' in request.form and request.form['action'] == 'close':
            return redirect(url_for('gioco.index'))

        if oggetto_selezionato and bersaglio_id:
            oggetto = next((o for o in inventario_pg.oggetti if o.nome == oggetto_selezionato), None)
            bersaglio = bersagli_dict.get(bersaglio_id)
            if oggetto and bersaglio:
                inventario_pg.usa_oggetto(oggetto, utilizzatore=pg_test, bersaglio=bersaglio)
                messaggio = Messaggi.get_messaggi()
                Messaggi.delete_messaggi()
            else:
                messaggio = "Oggetto o bersaglio non trovato!"

    oggetti = [{"nome": o.nome} for o in inventario_pg.oggetti]
    bersagli_view = [
        {
            "id": b.id,
            "nome": b.nome,
            "salute": b.salute,
            "salute_max": getattr(b, "salute_max", 100),
            "classe": b.__class__.__name__,
            "tipologia": "Sè stesso" if b is pg_test else "Alleato"
        }
        for b in bersagli
    ]

    return render_template(
        'inventory.html',
        pg_nome=pg_test.nome,
        oggetti=oggetti,
        oggetto_selezionato=oggetto_selezionato,
        bersagli=bersagli_view if oggetto_selezionato else [],
        messaggio=messaggio
    )