from flask import redirect, render_template, session, url_for, request, flash, jsonify
from . import battle_bp
from gioco.personaggio import Personaggio
from gioco.inventario import Inventario
from gioco.ambiente import Ambiente, Foresta
from gioco.missione import Missione, GestoreMissioni
from gioco.oggetto import Oggetto
from utils.messaggi import Messaggi
from utils.log import Log
import random
import json
import os

classi = {cls.__name__: cls for cls in Personaggio.__subclasses__()}

@battle_bp.route('/show_inventory', methods=['GET', 'POST'])
def show_inventory():
    # recupero dalla sessione il personaggio che sta giocando il turno corrente
    if 'personaggio_turno_corrente' in session:
        personaggio_turno_corrente = session['personaggio_turno_corrente']
        cls_pg_turno_corr = classi.get(personaggio_turno_corrente.get('classe'))
        if cls_pg_turno_corr:
                personaggio_turno_corrente = cls_pg_turno_corr.from_dict(personaggio_turno_corrente)

        #Recupero gli inventari dalla sessione cerco l'inventario del personaggio in turno e lo deserializzo
        inventari_des = []
        if 'inventari_selezionati' in session :
            inventari = session['inventari_selezionati']
            for inventario in inventari:
                if inventario['id_proprietario'] ==  personaggio_turno_corrente.id:
                    inventario = Inventario.from_dict(inventario)

    return render_template(
        'show_inventory.html',
        personaggio_turno_corrente=personaggio_turno_corrente,
        inventario=inventario)

@battle_bp.route('/begin_battle')
def begin_battle():
    # liste degli oggetti deserializzati
    print(session['missione'])
    personaggi_battle = []
    inventari_battle = []
    ambiente = Ambiente.from_dict(session['ambiente'])
    missione = Missione.from_dict(session['missione'])
    npc_list = missione.get_nemici

    if 'personaggi_selezionati' in session:
        personaggi = session['personaggi_selezionati']
        for pg in personaggi:
            # Deserializziamo i singoli oggetti e
            # inseriamoli nella lista personaggi_battle
            cls = classi.get(pg.get('classe'))
            if cls:
                personaggio = cls.from_dict(pg)
            personaggi_battle.append(personaggio)
    if 'inventari_selezionati' in session:
        inventari = session['inventari_selezionati']
        for inventario in inventari:
            inventario = Inventario.from_dict(inventario)
            inventari_battle.append(inventario)

    #TODO Personaggio turno è da riempire con personaggio a cui tocca il turno
    personaggio_turno_corrente = personaggi_battle[0]
    session['personaggio_turno_corrente'] = Personaggio.to_dict(personaggio_turno_corrente)

    return render_template(
        'begin_battle.html',
        personaggi=personaggi_battle,
        inventari=inventari_battle,
        ambiente=ambiente,
        missione=missione,
        personaggio_turno_corrente=personaggio_turno_corrente)


@battle_bp.route('/select_char', methods=['GET', 'POST'])
def select_char():
    # if request.method == 'POST':
    # prendo i dati da sessione:
    personaggi = []
    inventari = []
    missione_corrente = session['missione']
    if 'personaggi' in session and 'inventari' in session:
        pg_list = session.get('personaggi', [])
        inv_list = session.get('inventari',  [])
        # Deserializzo gli elementi delle liste
        """
        for serialized in  pg_list :
            personaggi.append(Personaggio.from_dict(serialized))
        for serialized in inv_list:
            inventari.append(Inventario.from_dict(serialized))
        #Ora le liste personaggi e  inventari contengono i dati deserializzati
        """
    # elementi_selezionati = request.form.getlist('personaggio_id')
    # if elementi_selezionati:
    #     for pg in pg_list:
    #         if pg['id'] in elementi_selezionati:
    #             personaggi.append(Personaggio.from_dict(pg))
    #             for inv in inv_list:
    #                 if pg == inv.proprietario:
    #                     inventari.append(Inventario.from_dict(inv))
    #                 break

    if request.method == 'POST':
        # Request.form.getlist restituisce una lista di stringhe
        indici_selezionati = request.form.getlist('selected_chars')
        personaggi_selezionati = []
        inventari_selezionati = []
        # se nel form passi l'indice iallora dobbiamo ricreare il personaggio per conservare i dati in sessione
        for idx in indici_selezionati:
            try:
                # creazione oggetti
                for pgs in pg_list:
                    if idx == pgs['id']:
                        cls = classi.get(pgs.get('classe'))
                        if cls:
                            pg = cls.from_dict(pgs)
                for invs in inv_list:
                    if invs['id_proprietario'] == idx:
                        inv = Inventario.from_dict(invs)
                # aggingiamo i personaggi alle liste
                print("PROVA", type(pg).__name__)
                personaggi_selezionati.append(pg)
                inventari_selezionati.append(inv)
            except (ValueError, IndexError):
                continue
        # serializzo le liste nella sessione
        session['personaggi_selezionati'] = [
            pg.to_dict() for pg in personaggi_selezionati]

        session['inventari_selezionati'] = [
            inv.to_dict() for inv in inventari_selezionati]

        # session['missione']= Missione.to_dict(missione_corrente)
        # reindirizzo verso la pagina di destinazione
        return redirect(url_for('battle.begin_battle'))
    # eventualmente carico selezione precedente per avere vaolri di default
    selezionati_pg = []
    selezionati_inv = []
    if 'personaggi_selezionati' in session:
        for sec in session['personaggi_selezionati']:
            cls = classi.get(sec.get('classe'))
            if cls:
                selezionati_pg.append(cls.from_dict(sec))
        for sec in session.get('inventari_selezionati', []):
            selezionati_inv.append(Inventario.from_dict(sec))

    return render_template(
        'select_char.html',
        personaggi=pg_list,
        inventari=inv_list,
        missione_corrente=missione_corrente,
        selezionati_pg=selezionati_pg,
        selezionati_inv=selezionati_inv)


@battle_bp.route('/test_battle', methods=['GET', 'POST'])
def test_battle():
    # --- SETUP DATI ---
    # Recupera o crea la lista unica di personaggi (giocatori + npc)
    if 'tutti_personaggi' not in session:
        tutti_personaggi = []
        if 'personaggi_selezionati' in session:
            for pg in session['personaggi_selezionati']:
                cls = classi.get(pg.get('classe'))
                if cls:
                    tutti_personaggi.append(cls.from_dict(pg))
        missione = Missione.from_dict(session['missione'])
        for nemico in missione.nemici:
            tutti_personaggi.append(nemico)
        session['tutti_personaggi'] = [p.to_dict() for p in tutti_personaggi]
        ordine_turni = list(range(len(tutti_personaggi)))
        random.shuffle(ordine_turni)
        session['ordine_turni'] = ordine_turni
        session['indice_turno_corrente'] = 0
        session['messaggi_battaglia'] = []
    else:
        tutti_personaggi = []
        for p in session['tutti_personaggi']:
            cls = classi.get(p.get('classe'))
            if cls:
                tutti_personaggi.append(cls.from_dict(p))

    ambiente = Ambiente.from_dict(session['ambiente'])
    missione = Missione.from_dict(session['missione'])
    inventari = []
    if 'inventari_selezionati' in session:
        for inv in session['inventari_selezionati']:
            inventari.append(Inventario.from_dict(inv))

    # --- TURNO CORRENTE ---
    ordine_turni = session['ordine_turni']
    indice_turno = session['indice_turno_corrente']
    idx_pg = ordine_turni[indice_turno]
    personaggio_turno_corrente = tutti_personaggi[idx_pg]

    # --- CONDIZIONI DI VITTORIA/SCONFITTA ---
    pc_vivi = [p for p in tutti_personaggi if not p.npc and not p.sconfitto()]
    npc_vivi = [p for p in tutti_personaggi if p.npc and not p.sconfitto()]
    battaglia_finita = False
    vittoria = False
    if not pc_vivi:
        battaglia_finita = True
        vittoria = False
        session['messaggi_battaglia'].append(
            "Tutti i personaggi sono stati sconfitti! Sconfitta!")
    elif not npc_vivi:
        battaglia_finita = True
        vittoria = True
        session['messaggi_battaglia'].append(
            "Tutti i nemici sono stati sconfitti! Vittoria!")

    # --- AZIONI TURNO GIOCATORE ---
    if request.method == 'POST' and not battaglia_finita:
        azione = request.form.get('azione')
        bersaglio_id = request.form.get('bersaglio_id')
        oggetto_nome = request.form.get('oggetto_nome')
        messaggi = session['messaggi_battaglia']

        # Trova bersaglio
        bersaglio = next((p for p in tutti_personaggi if p.id == bersaglio_id and not p.sconfitto()), None)
        if azione == 'attacco' and bersaglio:
            danno = personaggio_turno_corrente.attacca()
            bersaglio.subisci_danno(danno)
            messaggi.append(f"{personaggio_turno_corrente.nome} attacca {bersaglio.nome} per {danno} danni!")
            if bersaglio.sconfitto():
                messaggi.append(f"{bersaglio.nome} è stato sconfitto!")
        elif azione == 'usa_oggetto' and bersaglio and oggetto_nome:
            inventario = next((inv for inv in inventari if inv.id_proprietario == personaggio_turno_corrente.id), None)
            if inventario:
                oggetto = next((o for o in inventario.oggetti if o.nome == oggetto_nome), None)
                if oggetto:
                    risultato = inventario.usa_oggetto(oggetto, ambiente)
                    bersaglio.recupera_salute(risultato)
                    messaggi.append(f"{personaggio_turno_corrente.nome} usa {oggetto.nome} su {bersaglio.nome} per {risultato} HP!")
        elif 'salva_stato' in request.form:
            stato = {
                'tutti_personaggi': [p.to_dict() for p in tutti_personaggi],
                'ordine_turni': ordine_turni,
                'indice_turno_corrente': indice_turno,
                'messaggi_battaglia': messaggi
            }
            with open('data/battaglia_salvata.json', 'w', encoding='utf-8') as f:
                json.dump(stato, f, ensure_ascii=False, indent=2)
            flash('Stato battaglia salvato!', 'success')

        # Passa al prossimo turno vivo
        for _ in range(len(ordine_turni)):
            indice_turno = (indice_turno + 1) % len(ordine_turni)
            if not tutti_personaggi[ordine_turni[indice_turno]].sconfitto():
                break
        session['indice_turno_corrente'] = indice_turno
        session['tutti_personaggi'] = [p.to_dict() for p in tutti_personaggi]
        session['messaggi_battaglia'] = messaggi
        return redirect(url_for('battle.test_battle'))

    # --- AZIONE NPC ---
    if not battaglia_finita and personaggio_turno_corrente.npc:
        # Scegli un bersaglio valido (giocatore vivo)
        bersagli_validi = [p for p in tutti_personaggi if not p.npc and not p.sconfitto()]
        if bersagli_validi:
            bersaglio = random.choice(bersagli_validi)
            danno = personaggio_turno_corrente.attacca()
            bersaglio.subisci_danno(danno)
            session['messaggi_battaglia'].append(f"{personaggio_turno_corrente.nome} (NPC) attacca {bersaglio.nome} per {danno} danni!")
            if bersaglio.sconfitto():
                session['messaggi_battaglia'].append(f"{bersaglio.nome} è stato sconfitto!")
        # Passa al prossimo turno vivo
        for _ in range(len(ordine_turni)):
            indice_turno = (indice_turno + 1) % len(ordine_turni)
            if not tutti_personaggi[ordine_turni[indice_turno]].sconfitto():
                break
        session['indice_turno_corrente'] = indice_turno
        session['tutti_personaggi'] = [p.to_dict() for p in tutti_personaggi]
        return redirect(url_for('battle.test_battle'))

    # --- INVENTARIO DEL TURNO CORRENTE ---
    inventario_corrente = next((inv for inv in inventari if inv.id_proprietario == personaggio_turno_corrente.id), None)

    return render_template(
        'test_battle.html',
        tutti_personaggi=tutti_personaggi,
        ambiente=ambiente,
        missione=missione,
        personaggio_turno_corrente=personaggio_turno_corrente,
        inventario_corrente=inventario_corrente,
        battaglia_finita=battaglia_finita,
        vittoria=vittoria,
        messaggi=session.get('messaggi_battaglia', [])
    )