import os, json
from . import characters_bp
from flask import render_template, request, redirect, url_for, session, abort, flash
from gioco.personaggio import Personaggio
from gioco.oggetto import Oggetto
from gioco.inventario import Inventario
from utils.log import Log
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from auth.models import User
from auth.models import db
from credits.credits import credits_for_char
from config import DATA_DIR, CHAR_FILE


@characters_bp.route('/create_char', methods=['GET', 'POST'])
@login_required
def create_char():

    # provo a caricare (DESERIALIZZAZIONE) il contenuto JSON in una lista
    try:
        with open(CHAR_FILE, "r", encoding="utf-8") as file:
            # json.load legge e converte il testo JSON in oggetto (qui: lista di dizionari)
            characters = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # FileNotFoundError: file non esiste, JSONDecodeError: file vuoto/corrotto
        characters = []  # creazione lista vuota di personaggi
        os.makedirs(DATA_DIR, exist_ok=True)  # creazione dir se inesistente
        # serializzo lista vuota su file per inizializzarlo comunque
        with open(CHAR_FILE, "w", encoding="utf-8") as file:
            json.dump(characters, file, indent=4)

    from app import db
    # cattura dinamica di tutte le sottoclassi di Oggetto e Personaggio
    classi = {cls.__name__: cls for cls in Personaggio.__subclasses__()}
    oggetti = {cls.__name__: cls for cls in Oggetto.__subclasses__()}

    if request.method == 'POST':
        # lettura valori dal form
        nome = request.form['nome'].strip()
        classe_sel = request.form['classe']
        oggetto_sel = request.form['oggetto']

        # Controllo se ci sono almeno 10 crediti per eseguire la creazione di un personaggio
        CREDITI_NECESSARI_PERSONAGGIO = 20
        if current_user.crediti < CREDITI_NECESSARI_PERSONAGGIO:
            msg = f"Non hai abbastanza crediti per creare un personaggio (minimo richiesto: {CREDITI_NECESSARI_PERSONAGGIO})."
            flash(msg, "danger")
            return redirect(url_for('auth.area_personale'))
        else:
            current_user.crediti -= CREDITI_NECESSARI_PERSONAGGIO

        pg = classi[classe_sel](nome, npc=False)
        ogg = oggetti[oggetto_sel]()
        inv = Inventario(id_proprietario=pg.id)
        inv.aggiungi_oggetto(ogg)

        pg_list = session.get('personaggi', [])
        inv_list = session.get('inventari', [])

        pg_list.append(pg.to_dict())
        inv_list.append(inv.to_dict())

        # SERIALIZZAZIONE: aggiunta del nuovo personaggio alla lista obj
        characters.append(pg.to_dict())
        # scrittura del file JSON con il contenuto aggiornato di obj
        with open(CHAR_FILE, "w", encoding="utf-8") as file:
            json.dump(characters, file, indent=4)

        session['personaggi'] = pg_list
        session['inventari'] = inv_list
        character_ids = (current_user.character_ids or []) + [pg.id]
        current_user.character_ids = character_ids

        db.session.commit()
        Log.scrivi_log(f"Creato personaggio: {pg.nome}, Classe: {classe_sel}, id: {pg.id}, Oggetto iniziale: {oggetto_sel}")

        return redirect(url_for('characters.mostra_personaggi'))

    return render_template(
        'create_char.html',
        classi=list(classi.keys()),
        oggetti=list(oggetti.keys())
    )



@characters_bp.route('/edit_char/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_char(id):
    from app import db
    # mappa nomi-classi per poter permettere di cambiare classe
    classi = {cls.__name__: cls for cls in Personaggio.__subclasses__()}
    # prende valore associato a chiave 'personaggi' da sessione oppure lista vuota
    lista_pg = session.get('personaggi', [])
    try:
        # prova a recuperare il dizionario del pg da lista_pg tramite id
        pg_dict = lista_pg[id]
    except IndexError:
        flash("Impossibile trovare il personaggio desiderato")
        return redirect(url_for('characters.mostra_personaggi'))
    if request.method == 'POST':

        # otteniamo i valori dal form
        nuovo_nome = request.form['nome'].strip()
        nuova_classe = request.form['classe']

        vecchio_nome = pg_dict['nome']  # cattura vecchio nome a fini di log

        # ricreiamo istanza di personaggio con dati aggiornati
        pg_dict['nome'] = nuovo_nome
        pg_dict['classe'] = nuova_classe

        Log.scrivi_log(
            f"Modificato personaggio id={id}: "
            f"Nome: da '{vecchio_nome}' a '{nuovo_nome}', "
            f"Nuova classe: '{nuova_classe}'"
        )

        # salvataggio in sessione
        session['personaggi'] = lista_pg
        return redirect(url_for('characters.mostra_personaggi'))

    # mostra form precompilato
    return render_template(
        'edit_char.html',
        id=id,
        pg=pg_dict,
        classi=list(classi.keys())
    )


@characters_bp.route('/personaggi', methods=['GET', 'POST'])
def mostra_personaggi():
    lista_pers = session.get('personaggi', [])
    lista_pers_utente = []
    for pers in lista_pers:
        for per in current_user.character_ids:
            if per == pers['id']:
                lista_pers_utente.append(pers)
    Log.scrivi_log(f"Richiesta lista personaggi. Numero personaggi: {len(lista_pers)}, Personaggi: {lista_pers}")
    return render_template('list_char.html', personaggi = lista_pers )


@characters_bp.route('/personaggi/<int:id>')
def dettaglio_personaggio(id):
    lista_pers = session.get('personaggi', [])
    try:
        pg_dict = lista_pers[id]
        
        Log.scrivi_log(f"Visualizzazione dettagli personaggio con ID: {id}, Nome: {pg_dict["nome"]}")
    except IndexError:
        Log.scrivi_log(f"Tentativo di accesso a personaggio inesistente con ID: {id}")
        abort(404)
    return render_template('details_char.html', pg = pg_dict, id=id)


@characters_bp.route('/personaggi/<int:id>', methods=['POST'])
def elimina_personaggio(id):
    # CREDITI_RIMBORSATI = 20
    lista_pers = session.get('personaggi', [])
    try:
        pg = lista_pers.pop(id)
        session['personaggi'] = lista_pers

        # caricamento JSON da file
        with open(CHAR_FILE, 'r', encoding='utf-8') as f:
            characters = json.load(f)

        # rimozione elemento per indice
        characters.pop(id)

        # riscrittura file con lista aggiornata
        with open(CHAR_FILE, 'w', encoding='utf-8') as f:
            json.dump(characters, f, indent=4)

        Log.scrivi_log(f"Eliminato personaggio con ID: {pg.get('id')}, Nome: {pg.get('nome', 'N/A')}")

        # Questo pezzo di codice è commentato perché non è chiaro se si voglia rimborsare i crediti
        # current_user.crediti += CREDITI_RIMBORSATI
        # db.session.commit()
        # flash("Personaggio eliminato con successo!", "success")

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

        pg1 = Personaggio.from_dict(pg1_dict)
        pg2 = Personaggio.from_dict(pg2_dict)

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
