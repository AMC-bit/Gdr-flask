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
    bersaglio_id = request
    messaggio = None

    # Gestione della richiesta POST
    if request.method == 'POST':
        if 'action' in request.form and request.form['action'] == 'close':
            return redirect(url_for('gioco.index'))

    oggetto = request.form.get('oggetto')
    bersaglio_id = request.form.get('bersaglio')

    if oggetto:
        oggetto_selezionato = next(
            (o for o in inventario_pg.oggetti if o.nome == oggetto), None
        )
        if not oggetto_selezionato:
            flash(f"Oggetto '{oggetto}' non trovato nell'inventario.", 'error')
            return redirect(url_for('inventario.test_inventory'))
    if oggetto and bersaglio:
        oggetto_selezionato = next(
            (o for o in inventario_pg.oggetti if o.nome == oggetto), None
        )
        messaggio_completo = Messaggi.get_messaggi()
        righe = messaggio_completo.strip().split('\n')
        messaggio = '\n'.join(righe[-3:])  # Ottieni solo le ultime 3 righe
    else:
        messaggio = "Oggetto o bersaglio non trovato!"
        Messaggi.add_to_messaggi(messaggio)

    return render_template(
        'inventory.html',
        pg_nome=pg_test.nome,
        oggetti=inventario_pg.mostra_lista_inventario(),
        oggetto_selezionato=oggetto_selezionato,
        bersagli=bersagli,
        messaggio=messaggio
    )