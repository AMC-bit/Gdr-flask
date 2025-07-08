import os, json, logging
from . import characters_bp
from flask import render_template, request, redirect, url_for, session, abort, flash
from gioco.personaggio import Personaggio
from gioco.oggetto import Oggetto
from gioco.classi import PersonaggioSchema
from gioco.inventario import Inventario
from utils.log import Log
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from auth.models import User
from auth.models import db
from auth.credits import credits_to_create, credits_to_refund
from config import DATA_DIR

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

    if os.path.isdir(DATA_DIR):
        print("Cartella esistente")
    else:
        os.makedirs(DATA_DIR, exist_ok=True)

    files = os.listdir(DATA_DIR)
    print(DATA_DIR)

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
    path = os.path.join(DATA_DIR, name_file)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(pg_dict, file, indent=4)


@characters_bp.route('/create_char', methods=['GET', 'POST'])
@login_required
def create_char():

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
        ogg = oggetti[oggetto_sel]()
        inv = Inventario(id_proprietario=pg.id)
        inv.aggiungi_oggetto(ogg)

        # Controllo se ci sono almeno 10 crediti per eseguire la creazione di un personaggio
        costo_pg = credits_to_create(pg)
        if current_user.crediti < costo_pg:
            msg = f"Non hai abbastanza crediti per creare un personaggio (minimo richiesto: {costo_pg})."
            flash(msg, "danger")
            return redirect(url_for('auth.area_personale'))
        else:
            current_user.crediti -= costo_pg

        pg_list = session.get('personaggi', [])
        inv_list = session.get('inventari', [])

        pg_dict = schema.dump(pg)
        pg_list.append(pg_dict)

        inv_list.append(inv.to_dict())

        # Creazione del file JSON del singolo personaggio
        CharSingleJson(pg_dict)

        session['personaggi'] = pg_list
        session['inventari'] = inv_list
        character_ids = (current_user.character_ids or []) + [pg.id]
        current_user.character_ids = character_ids

        db.session.commit()
        logger.info(f"Creato personaggio: {pg.nome}, Classe: {classe_sel}, id: {pg.id}, Oggetto iniziale: {oggetto_sel}")

        return redirect(url_for('characters.mostra_personaggi'))

    return render_template(
        'create_char.html',
        classi=list(classi.keys()),
        oggetti=list(oggetti.keys())
    )


@characters_bp.route('/edit_char/<uuid:char_id>', methods=['GET', 'POST'])
@login_required
def edit_char(char_id):

    from app import db

    # prendo lista id personaggi posseduti
    owned_ids = load_char()
    # controllo che l'id del personaggio sia tra i personaggi posseduti
    if str(char_id) not in owned_ids:
        flash("Impossibile trovare il personaggio", "danger")
        return redirect(url_for("characters.mostra_personaggi"))

    # costruzione percorso file JSON
    path = os.path.join(DATA_DIR, f"{char_id}.json")
    # in caso di file JSON non trovato
    if not os.path.isfile(path):
        flash("Personaggio non raggiungibile")
        return redirect(url_for('characters.mostra_personaggi'))
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
        # ricreiamo istanza di personaggio con dati aggiornati
        pg_dict['nome'] = nuovo_nome
        pg_dict['classe'] = nuova_classe

        pg_obj = schema.load(pg_dict)
        pg_dict = schema.dump(pg_obj)
        CharSingleJson(pg_dict)

        logger.info(
            f"Modificato personaggio id={char_id}: "
            f"Nome: da '{vecchio_nome}' a '{nuovo_nome}', "
            f"Nuova classe: '{nuova_classe}'"
        )

        # conferma di avvenuto aggiornamento
        flash("Personaggio aggiornato con successo", "success")
        return redirect(url_for('characters.mostra_personaggi'))

    # mostra form precompilato
    return render_template(
        'edit_char.html',
        pg=pg_dict,
        classi=list(classi.keys())
    )


@characters_bp.route('/recupera_personaggi_posseduti')
def recupera_personaggi_posseduti(owned_chars):
    personaggi_posseduti = []
    for id in owned_chars :
        nome_file = id
        print(f"ID: {id}")
        #Recupero il path del file json del personaggio
        path = os.path.join(DATA_DIR, f"{nome_file}.json")

        with open (path, "r") as file:
            char_dict = json.load(file)
            personaggio = schema.load(char_dict)  # Deserializza il personaggio
            char_dict = schema.dump(personaggio)  # Serializza di nuovo per uniformità
            personaggi_posseduti.append(char_dict)
    return personaggi_posseduti


@characters_bp.route('/personaggi', methods=['GET'])
def mostra_personaggi():
    owned_chars = load_char()
    lista_pers_utente = recupera_personaggi_posseduti(owned_chars)
    logger.info(
        f"Richiesta lista personaggi. "
        f"Di questo utente: {len(lista_pers_utente)}"
    )
    return render_template(
        'list_char.html',
        personaggi=lista_pers_utente
    )
# -----

@characters_bp.route('/personaggi/<uuid:char_id>', methods=['GET'])
@login_required
def dettaglio_personaggio(char_id):
    # check cartella esistente
    os.makedirs(DATA_DIR, exist_ok=True)
    # deserializzazione
    try:
        owned_chars = load_char()
        lista_pers = recupera_personaggi_posseduti(owned_chars)
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
        'details_char.html',
        pg=pg_dict,
        id=char_id
    )


@characters_bp.route('/personaggi/<int:id>', methods=['POST'])
def elimina_personaggio(id):

    lista_pers = session.get('personaggi', [])
    try:
        pg = lista_pers.pop(id)
        session['personaggi'] = lista_pers

        # Eliminiamo unicamente il file json con l'id del personaggio
        file_path = os.path.join(DATA_DIR, f"{pg.get('id')}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File JSOn eliminato: {file_path}")
        else:
            logger.info("File JSON non trovato.")

        logger.info(f"Eliminato personaggio con ID: {pg.get('id')}, Nome: {pg.get('nome', 'N/A')}")

        # Rimozione esplicita dell'id da current_user.character_ids
        ids = current_user.character_ids or []  # lista id
        nuova_lista = []

        for c_id in ids:  # controllo tutti gli id esistenti in lista
            if c_id != pg.get('id'):  # se non è quello da rimuovere
                nuova_lista.append(c_id)  # lo aggiungo alla nuova lista

        current_user.character_ids = nuova_lista  # assegno la lista filtrata

        # Ricostruzione del personaggio per in modo a passare al metodo credits_to_refund
        classi = {cls.__name__: cls for cls in Personaggio.__subclasses__()}
        try:
            pg_ogg = classi.get(pg['classe'])(pg['nome'])
        except (KeyError. AttributeError, TypeError) as e:
            raise ValueError(f"Errore nella creazione del personaggio: {e}")

        current_user.crediti += credits_to_refund(pg_ogg)
        db.session.commit()
        flash("Personaggio eliminato con successo!", "success")

    except IndexError:
        Log.scrivi_log(f"Errore durante eliminazione: ID inesistente {pg.get('id')}")
        abort(404)
    return redirect(url_for('characters.mostra_personaggi'))


@characters_bp.route('/combattimento', methods=['GET', 'POST'])
def inizio_combattimento():
    lista_pers = session.get('personaggi', [])
    personaggi_utente = [p for p in lista_pers if p['id'] in (current_user.character_ids or [])]

    if request.method == 'POST':
        id_1 = int(request.form['pg1'])
        id_2 = int(request.form['pg2'])


        pg1_dict = next((p for p in personaggi_utente if p['id'] == id_1), None)
        pg2_dict = next((p for p in personaggi_utente if p['id'] == id_2), None)

        if not pg1_dict or not pg2_dict:
            abort(400, "Personaggio non trovato.")

        pg1 = schema.load(pg1_dict)
        pg2 = schema.load(pg2_dict)

        log_combattimento = []

        while pg1.salute > 0 and pg2.salute > 0:
            log_combattimento.append(f"Turno {turno}:")

            danno1 = pg1.attacca()
            pg2.subisci_danno(danno1)
            log_combattimento.append(f"{pg1.nome} infligge {danno1} danni a {pg2.nome} (Salute residua: {pg2.salute})")

            if pg2.salute <= 0:
                break

            danno2 = pg2.attacca()
            pg1.subisci_danno(danno2)
            log_combattimento.append(f"{pg2.nome} infligge {danno2} danni a {pg1.nome} (Salute residua: {pg1.salute})")

            turno += 1

        if pg1.salute > pg2.salute:
            risultato = f"Vittoria di {pg1.nome}!"
        elif pg2.salute > pg1.salute:
            risultato = f"Vittoria di {pg2.nome}!"
        else:
            risultato = "Pareggio!"

        log_combattimento.append(f"Risultato finale: {risultato}")
        Log.scrivi_log(f"Combattimento terminato - {risultato}")

        return render_template(
            'test_battle.html',
            pg1=pg1,
            pg2=pg2,
            risultato=risultato,
            log_combattimento=log_combattimento
        )

    return render_template('test_battle.html', personaggi=personaggi_utente)
