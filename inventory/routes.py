from . import inventory_bp
from flask import render_template, request, session, flash, redirect, url_for
from gioco.oggetto import Oggetto
from gioco.personaggio import Personaggio
from gioco.inventario import Inventario
from gioco.schemas.oggetto import OggettoSchema
from gioco.schemas.inventario import InventarioSchema
from flask_login import login_required
from marshmallow import ValidationError
import logging
from config import DATA_DIR_INV
import os, json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def salva_inventario_su_json(inventario: Inventario):
    """_summary_

    Args:
        inventario (Inventario): _description_
    """

    file_name = (
        f"{inventario.id_proprietario}.json"
        if inventario.id_proprietario else
        f"{inventario.id}.json"
    )
    file_path = os.path.join(DATA_DIR_INV, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(inventario.to_dict(), f, indent=4)

    logger.info(f"Inventario salvato in {file_name}")

def carica_inventario_da_json(personaggio_id):
    """Carica un inventario JSON direttamente dal file <id_proprietario>.json o fallback su id generico."""
    inventario_schema = InventarioSchema()

    # Prova file col nome dell'id_proprietario (comportamento principale)
    file_name = os.path.join(DATA_DIR_INV, f"{personaggio_id}.json")
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return inventario_schema.dump(
                    inventario_schema.load(data)
                )
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Errore nel caricamento del file {file_name}: {e}")
            return None

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
def add_object():
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

@inventory_bp.route('/delete-object/<string:oggetto_id>', methods=['POST'])
@login_required
def delete_object(oggetto_id):
    # Recupera ID del personaggio dal form nascosto (html)
    personaggio_id = request.form.get('personaggio_id')

    if not personaggio_id:
        flash("ID personaggio mancante", "danger")
        return redirect(url_for('inventory.inventory'))

    # Recupera dalla sessione la lista di personaggi e inventari
    personaggi = session.get('personaggi', [])
    inventari = session.get('inventari', [])

    # Ricostruiamo il personaggio e il suo inventario
    personaggio = next((p for p in personaggi if p['id'] == personaggio_id), None)
    inventario_pg = next((inv for inv in inventari if inv['id_proprietario'] == personaggio_id), None)

    if not personaggio or not inventario_pg:
        flash("Personaggio o inventario non trovato", "danger")
        return redirect(url_for('inventory.inventory'))

    # Creiamo uno schema per deserializzare l'inventario da dizionario a oggetto
    inventario_schema = InventarioSchema()
    try:
        # Converte il dizionario in un oggetto Inventario
        inventario_obj = inventario_schema.load(inventario_pg)
    except ValidationError as err:
        # Se c'è un errore nella deserializzazione, lo registriamo e mostriamo un errore
        logger.error(f"Errore deserializzazione inventario: {err}")
        flash("Errore nel caricamento dell'inventario", "danger")
        return redirect(url_for('inventory.inventory'))

    oggetto_rimosso = inventario_obj.rimuovi_oggetto(oggetto_id)

    if not oggetto_rimosso:
        flash("Oggetto non trovato nell'inventario", "warning")
        return redirect(url_for('inventory.inventory', personaggio_id=personaggio_id))

    inventario_aggiornato = inventario_schema.dump(inventario_obj)

    # Sostituiamo l'inventario vecchio con quello aggiornato nella sessione
    session['inventari'] = [
        inv if inv['id_proprietario'] != personaggio_id else inventario_aggiornato
        for inv in inventari
    ]

    logger.info(f"Oggetto con ID {oggetto_id} rimosso da {personaggio['nome']}")
    flash(f"Oggetto rimosso correttamente da {personaggio['nome']}", "success")

    return redirect(url_for('inventory.inventory', personaggio_id=personaggio_id))


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
