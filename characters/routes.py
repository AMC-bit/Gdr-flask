from . import characters_bp
from flask import render_template, request, redirect, url_for, session, abort
from gioco.personaggio import Personaggio
from gioco.oggetto import Oggetto
from gioco.inventario import Inventario
from utils.log import Log
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import json
@characters_bp.route('/create_char', methods=['GET', 'POST'])
def create_char():
    from app import db
    classi = {cls.__name__: cls for cls in Personaggio.__subclasses__()}
    oggetti = {cls.__name__: cls for cls in Oggetto.__subclasses__()}

    if request.method == 'POST':
        nome = request.form['nome'].strip()
        classe_sel = request.form['classe']
        oggetto_sel = request.form['oggetto']

        pg = classi[classe_sel](nome)
        ogg = oggetti[oggetto_sel]()
        inv = Inventario(id_proprietario=pg.id)
        inv.aggiungi_oggetto(ogg)

        pg_list = session.get('personaggi', [])
        inv_list = session.get('inventari', [])

        pg_list.append(pg.to_dict())
        inv_list.append(inv.to_dict())

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


@characters_bp.route('/personaggi', methods=['GET', 'POST'])
def mostra_personaggi():
    lista_pers = session.get('personaggi', [])
    lista_pers_utente = []
    for pers in lista_pers:
        for per in current_user.character_ids:
            if per == pers['id']:
                lista_pers_utente.append(pers)
    personaggi = [Personaggio.from_dict(pg) for pg in lista_pers_utente]
    Log.scrivi_log(f"Richiesta lista personaggi. Numero personaggi: {len(personaggi)}")
    return render_template('list_char.html', personaggi=personaggi)


@characters_bp.route('/personaggi/<int:id>')
def dettaglio_personaggio(id):
    lista_pers = session.get('personaggi', [])
    try:
        pg_dict = lista_pers[id]
        pg = Personaggio.from_dict(pg_dict)
        Log.scrivi_log(f"Visualizzazione dettagli personaggio con ID: {pg.id}, Nome: {pg.nome}")
    except IndexError:
        Log.scrivi_log(f"Tentativo di accesso a personaggio inesistente con ID: {id}")
        abort(404)
    return render_template('details_char.html', pg=pg, id=id)

@characters_bp.route('/personaggi/<int:id>', methods=['POST'])
def elimina_personaggio(id):
    lista_pers = session.get('personaggi', [])
    try:
        pg = lista_pers.pop(id)
        session['personaggi'] = lista_pers
        Log.scrivi_log(f"Eliminato personaggio con ID: {pg.get('id')}, Nome: {pg.get('nome', 'N/A')}")
    except IndexError:
        Log.scrivi_log(f"Errore durante eliminazione: ID inesistente {pg.get('id')}")
        abort(404)
    return redirect(url_for('characters.mostra_personaggi'))


@characters_bp.route('/combattimento', methods=['GET', 'POST'])
def inizio_combatimento():
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
