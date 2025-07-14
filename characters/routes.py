import os, json, logging
from . import characters_bp
from flask import render_template, request, redirect, url_for, session, abort, flash
from gioco.personaggio import Personaggio
from gioco.oggetto import Oggetto
from gioco.schemas.personaggio import PersonaggioSchema
from gioco.inventario import Inventario
from utils.log import Log
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from auth.models import User
from auth.models import db
from auth.credits import credits_to_create, credits_to_refund
from config import DATA_DIR_PGS, DATA_DIR_INV, CreateDirs

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
schema = PersonaggioSchema()


@characters_bp.route('/load_char')
@login_required
def load_char():
    # DESERIALIZZAZIONE
    # provo a leggere il contenuto della cartella json
    # ciclo su ogni file e ne estraggo i nomi
    # confronto i nomi dei file con i valori 'character_ids' del db
    # aggiungo i match a una lista

    all_char_json = []
    user_char = []
    owned_char = []

    files = os.listdir(DATA_DIR_PGS)
    print(DATA_DIR_PGS)

    for file in files:
        filename = os.path.splitext(file)[0]
        all_char_json.append(filename)

    for char_id in current_user.character_ids:
        user_char.append(char_id)

    print(f"all_char_json: {all_char_json}")
    print(f"user_char: {user_char}")

    # scorro la lista 'all_char_json' e includo solo gli elementi che sono anche nella lista 'user_char'
    owned_char = [c for c in all_char_json if c in user_char]

    # caso in cui l'utente non abbia id posseduti
    if not owned_char:
        return []

    # for c in all_char_json:
    #     if c in user_char:
    #         owned_char.append(c)
    print(f"owned_char: {owned_char}")

    return owned_char


def CharSingleJson(pg_dict: dict):
    # Recuperare i dati dal form per singolo personaggio
    # Creazione del file JSON con l'id del personaggio
    name_file = f"{pg_dict['id']}.json"
    path = os.path.join(DATA_DIR_PGS, name_file)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(pg_dict, file, indent=4)


@characters_bp.route('/create_char', methods=['GET', 'POST'])
@login_required
def create_char():

    CreateDirs()  # check cartelle esistenti

    from app import db
    # cattura dinamica di tutte le sottoclassi di Oggetto e Personaggio
    classi = {cls.__name__: cls for cls in Personaggio.__subclasses__()}
    oggetti = {cls.__name__: cls for cls in Oggetto.__subclasses__()}

    if request.method == 'POST':
        # lettura valori dal form
        nome = request.form['nome'].strip()
        classe_sel = request.form['classe']
        oggetto_sel = request.form['oggetto']

        pg = classi[classe_sel]()
        pg.nome = nome
        pg.npc = False
        pg.classe = classe_sel
        ogg = oggetti[oggetto_sel]()
        inv = Inventario(id_proprietario=pg.id)
        inv.aggiungi_oggetto(ogg)

        # Controllo se ci sono almeno 10 crediti per eseguire la creazione di un personaggio
        costo_pg = credits_to_create(pg)
        if current_user.crediti < costo_pg:
            msg = f"Non hai abbastanza crediti per creare un personaggio (minimo richiesto: {costo_pg})."
            flash(msg, "danger")
            return redirect(url_for('auth.personal_area'))
        else:
            current_user.crediti -= costo_pg

        pg_dict = schema.dump(pg)

        # Creazione del file JSON del singolo personaggio
        CharSingleJson(pg_dict)

        # Assicura che tutti gli id siano stringhe
        character_ids = (current_user.character_ids or []) + [str(pg.id)]
        current_user.character_ids = [str(cid) for cid in character_ids]

        db.session.commit()
        logger.info(f"Creato personaggio: {pg.nome}, Classe: {classe_sel}, id: {pg.id}, Oggetto iniziale: {oggetto_sel}")

        return redirect(url_for('characters.show_chars'))

    return render_template(
        'create_char.html',
        classi=list(classi.keys()),
        oggetti=list(oggetti.keys())
    )


@characters_bp.route('/edit_char/<uuid:char_id>', methods=['GET', 'POST'])
@login_required
def edit_char(char_id):

    # prendo lista id personaggi posseduti
    owned_ids = load_char()
    # controllo che l'id del personaggio sia tra i personaggi posseduti
    if str(char_id) not in owned_ids:
        flash("Impossibile trovare il personaggio", "danger")
        return redirect(url_for("characters.show_chars"))

    # costruzione percorso file JSON
    path = os.path.join(DATA_DIR_PGS, f"{char_id}.json")
    # in caso di file JSON non trovato
    if not os.path.isfile(path):
        flash("Personaggio non raggiungibile")
        return redirect(url_for('characters.show_chars'))
    # andiamo a leggere il file designato
    with open(path, 'r', encoding='utf-8') as f:
        pg_dict = json.load(f)

    # mappa nomi-classi per poter permettere di cambiare classe
    classi = {cls.__name__: cls for cls in Personaggio.__subclasses__()}

    if request.method == 'POST':

        # cattura vecchio nome a fini di log
        vecchio_nome = pg_dict['nome']

        # otteniamo i valori dal form
        nuovo_nome = request.form['nome'].strip()
        nuova_classe = request.form['classe']

        id = pg_dict['id']
        pg_obj = classi[nuova_classe](
            nome=nuovo_nome,
            id=id,
            classe=nuova_classe
        )

        pg_dict = schema.dump(pg_obj)
        CharSingleJson(pg_dict)

        logger.info(
            f"Modificato personaggio id={char_id}: "
            f"Nome: da '{vecchio_nome}' a '{nuovo_nome}', "
            f"Nuova classe: '{nuova_classe}'"
        )

        # conferma di avvenuto aggiornamento
        flash("Personaggio aggiornato con successo", "success")
        return redirect(url_for('characters.show_chars'))

    # mostra form precompilato
    return render_template(
        'edit_char.html',
        pg=pg_dict,
        classi=list(classi.keys())
    )


@characters_bp.route('/get_owned_chars')
def get_owned_chars(owned_chars):
    personaggi_posseduti = []
    for id in owned_chars:
        nome_file = id
        print(f"ID: {id}")
        #Recupero il path del file json del personaggio
        path = os.path.join(DATA_DIR_PGS, f"{nome_file}.json")

        with open(path, "r") as file:
            char_dict = json.load(file)
            # deserializza il personaggio
            personaggio = schema.load(char_dict)
            # serializza di nuovo per uniformità
            char_dict = schema.dump(personaggio)
            personaggi_posseduti.append(char_dict)
    return personaggi_posseduti


@characters_bp.route('/characters', methods=['GET'])
def show_chars():
    owned_chars = load_char()
    lista_pers_utente = get_owned_chars(owned_chars)
    logger.info(
        f"Richiesta lista personaggi. "
        f"Di questo utente: {len(lista_pers_utente)}"
    )
    return render_template(
        'list_char.html',
        personaggi=lista_pers_utente
    )
# -----

@characters_bp.route('/characters/<uuid:char_id>', methods=['GET'])
@login_required
def char_details(char_id):
    # check cartella esistente
    os.makedirs(DATA_DIR_PGS, exist_ok=True)
    # deserializzazione
    try:
        owned_chars = load_char()
        lista_pers = get_owned_chars(owned_chars)
        print("LISTA", lista_pers)
    except (FileNotFoundError, json.JSONDecodeError):
        lista_pers = []

    # ricerca del personaggio tramite ID
    pg_dict = None  # conterrà il dizionario del pg trovato
    for p in lista_pers:  # prendo tutti i p dentro la lista di dizionari
        if str(p['id']) == str(char_id):  # char id viene preso da URL
            pg_dict = p  # in caso di corrispondenza il diz trovato diventa pg_dict
            break  # mi basta un solo match perché i pg non sono duplicabili

    if pg_dict is None:
        logger.warning(f"Tentativo di accesso a personaggio inesistente con ID: {char_id}")
        abort(404)

    logger.info(
        f"Visualizzazione dettagli personaggio con ID: {char_id}, Nome: {pg_dict.get('nome', 'N/A')}"
    )
    return render_template(
        'char_details.html',
        pg=pg_dict,
        id=char_id
    )


@characters_bp.route('/characters/<uuid:char_id>', methods=['POST'])
@login_required
def char_delete(char_id):

    # ricostruzione percorso file json del personaggio designato
    file_path = os.path.join(DATA_DIR_PGS, f"{char_id}.json")

    # in caso di file JSON non trovato
    if not os.path.isfile(file_path):
        flash("Personaggio non raggiungibile")
        return redirect(url_for('characters.show_chars'))

    # andiamo a leggere il file designato
    with open(file_path, 'r', encoding='utf-8') as f:
        pg_dict = json.load(f)

    # ricrea oggetto personaggio
    pg_obj = schema.load(pg_dict)

    # eliminazione del file JSON corrispondente
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"File JSON eliminato: {file_path}")
    else:
        logger.warning(f"File JSON non trovato: {file_path}")

    # rimozione UUID dalla lista di current_user
    new_id_list = []
    for cid in current_user.character_ids or []:
        if str(cid) != str(char_id):
            new_id_list.append(cid)
    current_user.character_ids = new_id_list

    # rimborso crediti
    current_user.crediti += credits_to_refund(pg_obj)

    db.session.commit()
    flash("Personaggio eliminato con successo!", "success")
    return redirect(url_for('characters.show_chars'))


@characters_bp.route('/combattimento', methods=['GET', 'POST'])
def begin_combat():
    lista_pers = session.get('personaggi', [])
    personaggi_utente = [p for p in lista_pers if p['id'] in (current_user.character_ids or [])]

    if request.method == 'POST':
        id_1 = request.form['pg1']
        id_2 = request.form['pg2']

        pg1_dict = next((p for p in personaggi_utente if p['id'] == id_1), None)
        pg2_dict = next((p for p in personaggi_utente if p['id'] == id_2), None)

        if not pg1_dict or not pg2_dict:
            abort(400, "Personaggio non trovato.")

        pg1 = schema.load(pg1_dict)
        pg2 = schema.load(pg2_dict)
        pg1 = schema.load(pg1_dict)
        pg2 = schema.load(pg2_dict)

        log_combattimento = []
        turno = 1

        while pg1.salute > 0 and pg2.salute > 0:
            log_combattimento.append(f"Turno {turno}:")

            successo = pg1.esegui_azione()
            if successo:
                danno1 = pg1.attacca()
                pg2.subisci_danno(danno1)
                log_combattimento.append(f"{pg1.nome} infligge {danno1} danni a {pg2.nome} (Salute residua: {pg2.salute})")
            else:
                log_combattimento.append(f"{pg1.nome} ha fallito l'attacco!")
            if pg2.salute <= 0:
                break

            successo = pg2.esegui_azione()
            if successo:
                danno2 = pg2.attacca()
                pg1.subisci_danno(danno2)
                log_combattimento.append(f"{pg2.nome} infligge {danno2} danni a {pg1.nome} (Salute residua: {pg1.salute})")
            else:
                log_combattimento.append(f"{pg2.nome} ha fallito l'attacco!")
            turno += 1

        if 0 >= pg2.salute:
            risultato = f"Vittoria di {pg1.nome}!"
        elif 0 >= pg1.salute:
            risultato = f"Vittoria di {pg2.nome}!"

        log_combattimento.append(f"Risultato finale: {risultato}")
        Log.scrivi_log(f"Combattimento terminato - {risultato}")

        return render_template(
            'combat.html',
            pg1=pg1,
            pg2=pg2,
            risultato=risultato,
            log_combattimento=log_combattimento
        )

    return render_template('combat.html', personaggi=personaggi_utente)
