from flask import redirect, render_template, session, url_for, request, flash
from . import battle_bp
from gioco.personaggio import Personaggio
from gioco.inventario import Inventario
from gioco.ambiente import Ambiente, Foresta
from gioco.missione import Missione, GestoreMissioni
classi = {cls.__name__: cls for cls in Personaggio.__subclasses__()}

@battle_bp.route('/show_inventory', methods=['GET', 'POST'])
def show_inventory():
    #recupero dalla sessione il personaggio che sta giocando il turno corrente
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
                if inventario['proprietario'] ==  personaggio_turno_corrente.id:
                    inventario = Inventario.from_dict(inventario)

    return render_template('show_inventory.html',
                           personaggio_turno_corrente = personaggio_turno_corrente,
                           inventario = inventario
                           )

@battle_bp.route('/begin_battle')
def begin_battle():
    #liste degli oggetti deserializzati
    print(session['missione'])
    personaggi_battle = []
    inventari_battle = []
    ambiente = Ambiente.from_dict(session['ambiente'])
    missione = Missione.from_dict(session['missione'])
    npc_list = missione.get_nemici

    if 'personaggi_selezionati' in session :
        personaggi = session['personaggi_selezionati']
        for pg in personaggi:
            #Deserializiamo i singoli oggetti e inseriamoli nella lista perrsonaggi_battle
            cls = classi.get(pg.get('classe'))
            if cls:
                personaggio = cls.from_dict(pg)
            personaggi_battle.append(personaggio)
    if 'inventari_selezionati' in session :
        inventari = session['inventari_selezionati']
        for inventario in inventari:
            inventario = Inventario.from_dict(inventario) 
            inventari_battle.append(inventario)

    #TODO Personaggio turno è da riempire con il personaggio a cui tocca il turno
    personaggio_turno_corrente = personaggi_battle[0]
    session['personaggio_turno_corrente']= Personaggio.to_dict(personaggio_turno_corrente)

    return render_template('begin_battle.html',
                           personaggi = personaggi_battle,
                           inventari = inventari_battle,
                           ambiente = ambiente,
                           missione = missione,
                           personaggio_turno_corrente = personaggio_turno_corrente
                           )

@battle_bp.route('/select_char', methods=['GET', 'POST'] )
def select_char():
    #if request.method == 'POST':
    #prendo i dati da sessione :
    personaggi=[]
    inventari=[]
    missione_corrente = session['missione']
    if 'personaggi' in session and 'inventari' in session:
        pg_list = session.get('personaggi', [])
        inv_list = session.get('inventari',  [])
        #Deserializzo gli elementi delle liste
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
                    if invs['proprietario'] == idx:
                        inv = Inventario.from_dict(invs)
                # aggingiamo i personaggi alle liste
                print("PROVA", type(pg).__name__)
                personaggi_selezionati.append(pg)
                inventari_selezionati.append(inv)
            except (ValueError, IndexError):
                continue
        # serializzo le liste nella sessione
        session['personaggi_selezionati'] = [pg.to_dict() for pg in personaggi_selezionati]
        session['inventari_selezionati'] = [inv.to_dict() for inv in inventari_selezionati]
        #session['missione']= Missione.to_dict(missione_corrente)
        # reindirizzo verso la pagina di destinazione
        return redirect(url_for('battle.begin_battle'))
    # eventualmente carico la selezione precedente per avere dei vaolri di default
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
        missione_corrente = missione_corrente,
        selezionati_pg = selezionati_pg,
        selezionati_inv = selezionati_inv
    )