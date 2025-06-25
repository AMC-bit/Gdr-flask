from . import mission_bp
from flask import render_template, session, request, redirect, url_for, flash
from gioco.missione import GestoreMissioni
from utils.log import Log


@mission_bp.route('/select_mission', methods=['GET', 'POST'])
def select_mission():
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

    msg = f"Missione mostrata: {missione.nome}"
    flash(msg, 'info')
    Log.scrivi_log(msg)
    return render_template(
        'show_mission.html',
        missione=missione,
        ambiente=ambiente
    )


@mission_bp.route('/missioni')
def mostra_missioni():
    missioni = GestoreMissioni.lista_missioni
    return render_template('missioni.html', missioni=missioni)


@mission_bp.route('/missione/attiva')
def missione_attiva():
    missione = GestoreMissioni.sorteggia()
    if missione:
        return render_template('missione_attiva.html', missione=missione)
    return "Non ci sono missioni attive o disponibili."


@mission_bp.route('/missioni/stato')
def stato_missioni():
    complete = GestoreMissioni.finita()
    return f"Tutte le missioni completate: {complete}"
