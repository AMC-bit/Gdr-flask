from . import inventory_bp
from flask import render_template, request, session, flash, redirect, url_for
from gioco.oggetto import Oggetto, OggettoSchema
from gioco.personaggio import Personaggio
from gioco.classi import Ladro, Mago, Guerriero
from gioco.inventario import Inventario
from gioco.schemas.inventorio import InventarioSchema
from utils.log import Log
from flask_login import login_required
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@inventory_bp.route('/inventory', methods=['GET', 'POST'])
def inventory():
    personaggi = session.get('personaggi', [])
    inventari = session.get('inventari', [])

    nome_per_id = {p['id']: p['nome'] for p in personaggi}

    id_selezionato = None
    id_passato = None
    inventario_selezionato = None
    personaggio = None
    if request.method == 'GET':
        id_passato = request.args.get('personaggio_id')
        personaggio = next(
            (p for p in personaggi if p['id'] == id_passato), None
        )
        if id_passato:
            for inv in inventari:
                if inv['id_proprietario'] == id_passato:
                    inventario_selezionato = inv
                    logger.info(
                        f"Inventario di {nome_per_id[id_passato]}"
                        "selezionato via GET."
                    )
                    break

    if request.method == 'POST':
        id_selezionato = request.form.get('personaggio_id')
        personaggio = next(
            (p for p in personaggi if p['id'] == id_selezionato), None
        )
        # Cerca l'inventario del personaggio selezionato
        for inv in inventari:
            if inv['id_proprietario'] == id_selezionato:
                inventario_selezionato = inv
                logger.info(f"Inventario di {nome_per_id[id_selezionato]} selezionato.")

                break

    return render_template(
        'inventory.html',
        personaggi=personaggi,
        nome_per_id=nome_per_id,
        id_selezionato=id_selezionato,
        id_passato=id_passato,
        inventario=inventario_selezionato,
        personaggio=personaggio
    )

@inventory_bp.route('/add_object', methods=['GET', 'POST'])
@login_required
def aggiungi_oggetto():
    oggetti_classes = {cls.__name__: cls for cls in Oggetto.__subclasses__()}
    inventario_schema = InventarioSchema()

    # Recuperiamo l'ID del personaggio selezionato
    personaggio_id = request.args.get('personaggio_id') or request.form.get('personaggio_id')
    if not personaggio_id:
        flash("ID personaggio mancante", "danger")
        return redirect(url_for('inventory.inventory'))

    personaggi = session.get('personaggi', [])
    inventari = session.get('inventari', [])

    # Ricostruiamo il personaggio e il suo inventario
    personaggio = next((p for p in personaggi if p['id'] == personaggio_id), None)
    inventario_pg = next((inv for inv in inventari if inv['id_proprietario'] == personaggio_id), None)

    if not personaggio or not inventario_pg:
        flash("Personaggio o inventario non trovato", "danger")
        return redirect(url_for('inventory.inventory'))

    # Gestiamo la request 
    if request.method == 'POST':
        oggetto_sel = request.form.get('oggetto')

        if oggetto_sel not in oggetti_classes:
            logger.warning(f"Oggetto selezionato non valido: {oggetto_sel}")
            flash("Oggetto non valido", "danger")
            return redirect(url_for('inventory.aggiungi_oggetto', personaggio_id=personaggio_id))

        nuovo_oggetto = oggetti_classes[oggetto_sel]()
        # Questo print è stato aggiunto solo per controllare la struttura di inventario_pg
        print(f"inventario_pg -----------------------------------> {inventario_pg}")

        try:
            inventario_obj = inventario_schema.load(inventario_pg)
        except ValidationError as err:
            logger.error(f"Errore deserializzazione inventario: {err}")
            flash("Errore nel caricamento dell'inventario", "danger")
            return redirect(url_for('inventory.inventory'))

        inventario_obj.aggiungi_oggetto(nuovo_oggetto)
        inventario_aggiornato = inventario_schema.dump(inventario_obj)

        session['inventari'] = [
            inv if inv['id_proprietario'] != personaggio_id else inventario_aggiornato
            for inv in inventari
        ]

        logger.info(f"Aggiunto oggetto '{nuovo_oggetto.nome}' a {personaggio['nome']}")
        flash(f"Oggetto '{nuovo_oggetto.nome}' aggiunto a {personaggio['nome']}", "success")
        return redirect(url_for('inventory.inventory', personaggio_id=personaggio_id))

    return render_template(
        'edit_object.html',
        oggetti=list(oggetti_classes.keys()),
        personaggio=personaggio,
        personaggio_id=personaggio_id
    )

"""
@inventory_bp.route('/elimina-oggetto/<int:oggetto_id>', methods=['POST'])
def elimina_oggetto(oggetto_id):
    # logica per eliminare l’oggetto
    return redirect(url_for())"""


"""
@inventory_bp.route('/test-inventory', methods=['GET', 'POST'])
def test_inventory():
    # 1. Ottieni i dati dalla sessione
    personaggi_data = session.get('personaggi', [])
    inventari_data = session.get('inventari', [])

    if not personaggi_data or not inventari_data:
        return "Sessione non valida o incompleta", 400

    # 2. Crea il personaggio principale dinamicamente
    main_pg_data = personaggi_data[0]
    classe_pg = main_pg_data['classe']
    pg_classi = {'Mago': Mago, 'Guerriero': Guerriero, 'Ladro': Ladro}
    pg_test = pg_classi[classe_pg](main_pg_data['nome'])
    pg_test.__dict__.update(main_pg_data)
    # importa attributi come salute, livello ecc.

    # 3. Crea inventario del personaggio
    inventario_pg_data = next((
        inv for inv in inventari_data if inv['proprietario'] == pg_test.id
    ), None)
    inventario_pg = Inventario(pg_test)
    inventario_pg.oggetti = []
    for oggetto_data in inventario_pg_data['oggetti']:
        classe_oggetto = globals().get(oggetto_data['classe'])
        if classe_oggetto:
            oggetto = classe_oggetto()
            oggetto.__dict__.update(oggetto_data)
            inventario_pg.oggetti.append(oggetto)

    # 4. Crea bersagli (tutti i personaggi della sessione)
    bersagli = []
    bersagli_dict = {}
    for p_data in personaggi_data:
        cls = pg_classi.get(p_data['classe'])
        if cls:
            p = cls(p_data['nome'])
            p.__dict__.update(p_data)
            bersagli.append(p)
            bersagli_dict[p.id] = p

    # 5. Gestione POST
    oggetto_selezionato = request.form.get('oggetto')
    bersaglio_id = request.form.get('bersaglio')
    messaggio = None

    if request.method == 'POST':
        if 'action' in request.form and request.form['action'] == 'close':
            return redirect(url_for('gioco.index'))

        if oggetto_selezionato and bersaglio_id:
            oggetto = next((
                o for o in inventario_pg.oggetti
                if o.nome == oggetto_selezionato
            ), None)
            bersaglio = bersagli_dict.get(bersaglio_id)
            if oggetto and bersaglio:
                inventario_pg.usa_oggetto(
                    oggetto,
                    utilizzatore=pg_test,
                    bersaglio=bersaglio
                )
                messaggio = Messaggi.get_messaggi()
                Messaggi.delete_messaggi()
            else:
                messaggio = "Oggetto o bersaglio non trovato!"

    # 6. Prepara i dati per il template
    oggetti = [{"nome": o.nome} for o in inventario_pg.oggetti]
    bersagli_view = [
        {
            "id": b.id,
            "nome": b.nome,
            "salute": b.salute,
            "salute_max": getattr(b, "salute_max", 100),
            "classe": b.__class__.__name__,
            "tipologia": "Sè stesso" if b.id == pg_test.id else "Alleato"
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
    """
