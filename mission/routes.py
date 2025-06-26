from . import mission_bp
from flask import abort, flash, redirect, render_template, request, session, url_for
from gioco.missione import GestoreMissioni, Missione
from gioco.ambiente import Ambiente
from utils.messaggi import Messaggi
from utils.log import Log

@mission_bp.route('/select-mission', methods=['GET', 'POST'])
def select_mission():
    gestore = GestoreMissioni()
    missioni = {str(m.id): m for m in gestore.lista_missioni}

    if request.method == 'POST':
        missione_id = request.form.get("missione-id")
        missione = missioni.get(missione_id)
        if missione:
            session['missione'] = missione.to_dict()
            session['ambiente'] = missione.ambiente.to_dict()
            msg = f"Missione selezionata: {missione.nome}, ID: {missione.id}"
            Log.scrivi_log(msg)
            Messaggi.add_to_messaggi(msg)
            return redirect(url_for('mission.show_mission'))
        else:
            msg = "Missione non trovata."
            Log.scrivi_log(msg)
            Messaggi.add_to_messaggi(msg)
            flash(msg, 'error')

    return render_template('select_mission.html', missioni=missioni)

@mission_bp.route('/show-mission')
def show_mission():
    missione_data = session.get('missione')
    if not missione_data:
        msg = "Nessuna missione selezionata."
        Log.scrivi_log(msg)
        Messaggi.add_to_messaggi(msg)
        return redirect(url_for('mission.select_mission'))

    missione = Missione.from_dict(missione_data)
    ambiente_data = session.get('ambiente')
    if not ambiente_data:
        ambiente_missione = missione.ambiente
        session['ambiente'] = ambiente_missione.to_dict()
    elif ambiente_data != missione.ambiente.to_dict():
        session['ambiente'] = missione.ambiente.to_dict()

    msg = f"Mostra missione: {missione.nome}, ID: {missione.id}"
    msg += f"\nAmbiente: {missione.ambiente.nome}"
    flash(msg, 'info')
    Log.scrivi_log(msg)
    return render_template('show_mission.html', missione=missione)


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
