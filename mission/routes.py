from collections import defaultdict

from environment import routes as environment_routes
from . import mission_bp
from flask import flash, redirect, render_template, request, session, url_for, session, request, redirect, url_for, flash
from gioco.missione import GestoreMissioni, Missione
from utils.messaggi import Messaggi
from utils.log import Log
from utils.log import Log


@mission_bp.route('/select_mission', methods=['GET', 'POST'])
def select_mission():
    """
    Gestisce la selezione di una missione da parte dell'utente.
    Se l'utente seleziona una missione, la salva nella sessione e reindirizza alla pagina di visualizzazione della missione.
    Se non ci sono missioni disponibili, mostra un messaggio di errore.
    Se non è stata selezionata alcuna missione, mostra un messaggio di avviso.
    Se non esiste un gestore di missioni nella sessione, ne crea uno nuovo e lo salva nella sessione.
    Seleziona una missione dalla lista delle missioni disponibili e la salva nella sessione.
    Dalla missione selezionata, salva anche l'ambiente associato nella sessione.

    Returns:
        Renderizza il template 'select_mission.html' con la lista delle missioni disponibili.
        Se una missione è stata selezionata, reindirizza alla pagina di visualizzazione della missione.
    """
    if request.method == 'POST':
        missione_id = request.form.get('missione_id')

        # Recupera il gestore dalla sessione
        gestore_data = session.get('gestore_missioni')
        if not gestore_data:
            msg = 'Errore: gestore missioni non trovato in sessione.'
            flash(msg, 'error')
            Log.scrivi_log(msg)
            return redirect(url_for('mission.select_mission'))

        # Ricostruisce il gestore dalla sessione
        gestore = GestoreMissioni.from_dict(gestore_data)

        # Debug: stampa il missione_id ricevuto
        msg = f"DEBUG: missione_id ricevuto: '{missione_id}'"
        flash(msg, 'info')
        Log.scrivi_log(msg)

        # Trova la missione con l'ID specificato
        missione_selezionata = None
        for missione in gestore.lista_missioni:
            msg = f"DEBUG: Confronto '{str(missione.id)}' con '{missione_id}'"
            flash(msg, 'info')
            Log.scrivi_log(msg)
            if str(missione.id) == missione_id:
                missione_selezionata = missione
                break

        if missione_selezionata:
            # Salva missione e ambiente in sessione
            session['missione'] = missione_selezionata.to_dict()
            session['ambiente'] = missione_selezionata.ambiente.to_dict()

            msg = f"Missione selezionata: {missione_selezionata.nome}"
            flash(msg, 'success')
            Log.scrivi_log(msg)
            return redirect(url_for('mission.show_mission'))
        else:
            msg = 'Missione non trovata.'
            flash(msg, 'error')
            Log.scrivi_log(msg)

    # GET: mostra il form di selezione
    if 'gestore_missioni' not in session:
        gestore = GestoreMissioni()
        # Salva il gestore in sessione per mantenerlo coerente
        session['gestore_missioni'] = gestore.to_dict()
    else:
        # Ricostruisce il gestore dalla sessione
        gestore = GestoreMissioni.from_dict(session['gestore_missioni'])
    missioni = {
        str(missione.id): missione for missione in gestore.lista_missioni
    }
    return render_template('select_mission.html', missioni=missioni)


@mission_bp.route('/show_mission')
def show_mission():
    """
    Mostra i dettagli della missione selezionata.
    Se non è stata selezionata alcuna missione, mostra un messaggio di errore.


    """
    missione_data = session.get('missione')
    ambiente_data = session.get('ambiente')

    if not missione_data or not ambiente_data:
        msg = 'Nessuna missione selezionata.'
        flash(msg, 'error')
        Log.scrivi_log(msg)
        return redirect(url_for('mission.select_mission'))

    # Ricostruisce gli oggetti dai dati in sessione
    from gioco.missione import Missione
    from gioco.ambiente import Ambiente

    missione = Missione.from_dict(missione_data)
    ambiente = Ambiente.from_dict(ambiente_data)
    premi = missione.premi
    premi_raggruppati = defaultdict(list)
    for premio in premi:
        premi_raggruppati[premio.nome].append(premio)

    msg = f"Missione mostrata: {missione.nome}"
    flash(msg, 'info')
    Log.scrivi_log(msg)
    environment_routes.descrizione()
    return render_template(
        'show_mission.html',
        missione=missione,
        ambiente=ambiente,
        premi_raggruppati=premi_raggruppati
    )



@mission_bp.route('/missioni')
def mostra_missioni():
    missioni = GestoreMissioni.lista_missioni
    return render_template('missioni.html', missioni=missioni)


@mission_bp.route('/missione/attiva')
def missione_attiva():
    gestore = GestoreMissioni()
    if 'missione' in session:
        missione_data = session['missione']
        missione = Missione.from_dict(missione_data)
        if missione.attiva:
            return render_template('missione_attiva.html', missione=missione)
    missione = gestore.sorteggia()
    if missione and missione.attiva:
        msg = f"Missione attiva: {missione.nome}, ID: {missione.id}"
        Log.scrivi_log(msg)
        return render_template('missione_attiva.html', missione=missione)
    Log.scrivi_log("Nessuna missione attiva al momento.")
    flash("Non ci sono missioni attive o disponibili.", 'warning')
    return redirect(url_for('mission.select_mission'))


@mission_bp.route('/missioni/stato')
def stato_missioni():
    gestore = GestoreMissioni()
    complete = gestore.finita()
    if complete:
        msg = "Tutte le missioni sono state completate."
        Log.scrivi_log(msg)
        Messaggi.add_to_messaggi(msg)
    else:
        msg = "Ci sono missioni ancora da completare."
        Log.scrivi_log(msg)
        Messaggi.add_to_messaggi(msg)
