from flask import redirect, render_template, session, url_for, request
from . import battle_bp
from gioco.personaggio import Personaggio
from gioco.inventario import Inventario
from gioco.ambiente import Ambiente, Foresta
from gioco.missione import Missione, GestoreMissioni

@battle_bp.route('/begin_battle')
def begin_battle():
    #liste degli oggetti deserializzati
    print(session['personaggi_selezionati'], session['inventari_selezionati'] )
    personaggi_battle = []
    inventari_battle = []
    ambiente = Ambiente.from_dict(session['ambiente'])
    missione = Missione.from_dict(session['missione'])
    
    if 'personaggi_selezionati' in session :
        personaggi = session['personaggi_selezionati']
        for personaggio in personaggi:
            #Deserializiamo i singoli oggetti e inseriamoli nella lista perrsonaggi_battle
            personaggio = Personaggio.from_dict(personaggio)
            personaggi_battle.append(personaggio)
    if 'inventari_selezionati' in session :
        inventari = session['inventari_selezionati']
        for inventario in inventari:
            inventario = Inventario.from_dict(inventario) 
            inventari_battle.append(inventario)
    
    return render_template('begin_battle.html',
                           personaggi = personaggi_battle,
                           inventari = inventari_battle,
                           ambiente = ambiente,
                           missione = missione)

@battle_bp.route('/select_char', methods=['GET', 'POST'] )
def select_char():
    #if request.method == 'POST':

    #prendo i dati da sessione :
    personaggi=[]
    inventari=[]
    ambiente = Foresta()
    gestore_missioni = GestoreMissioni()
    missione_corrente = gestore_missioni.sorteggia()
    if 'ambiente' in session :
        #Recupero l'oggetto ambiente dalla sessione deserializzandolo
        ambiente = Ambiente.from_dict(session['ambiente'])
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
                        pg = Personaggio.from_dict(pgs)
                for invs in inv_list:
                    if invs['proprietario'] == idx:
                        inv = Inventario.from_dict(invs)
                # aggingiamo i personaggi alle liste
                personaggi_selezionati.append(pg)
                inventari_selezionati.append(inv)
            except (ValueError, IndexError):
                continue
        # serializzo le liste nella sessione
        session['personaggi_selezionati'] = [pg.to_dict() for pg in personaggi_selezionati]
        session['inventari_selezionati'] = [inv.to_dict() for inv in inventari_selezionati]
        session['missione']= Missione.to_dict(missione_corrente)
        # reindirizzo verso la pagina di destinazione
        return redirect(url_for('battle.begin_battle'))
    # eventualmente carico la selezione precedente per avere dei vaolri di default
    selezionati_pg = []
    selezionati_inv = []
    if 'personaggi_selezionati' in session:
        for sec in session['personaggi_selezionati']:
            selezionati_pg.append(Personaggio.from_dict(sec))
        for sec in session.get('inventari_selezionati', []):
            selezionati_inv.append(Inventario.from_dict(sec))


    return render_template(
        'select_char.html',
        personaggi=pg_list,
        inventari=inv_list,
        ambiente_corrente = ambiente,
        missione_corrente = missione_corrente,
        selezionati_pg = selezionati_pg,
        selezionati_inv = selezionati_inv
    )