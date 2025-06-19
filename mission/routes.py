from . import mission_bp
from flask import render_template
from gioco.missione import gestore_missioni

@mission_bp.route('/select_mission')
def select_mission():
    return render_template('select_mission.html')

@mission_bp.route('/missioni')
def mostra_missioni():
    missioni = gestore_missioni.lista_missioni
    return render_template('missioni.html', missioni=missioni)


@mission_bp.route('/missione/attiva')
def missione_attiva():
    missione = gestore_missioni.sorteggia()
    if missione:
        return render_template('missione_attiva.html', missione=missione)
    return "Non ci sono missioni attive o disponibili."


@mission_bp.route('/missioni/stato')
def stato_missioni():
    complete = gestore_missioni.finita()
    return f"Tutte le missioni completate: {complete}"
