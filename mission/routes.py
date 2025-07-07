from collections import defaultdict

from . import mission_bp
from flask import flash, render_template, request, session, \
    redirect, url_for
from gioco.missione import GestoreMissioni, Missione
from utils.messaggi import Messaggi
from utils.log import Log


@mission_bp.route('/select_mission', methods=['GET', 'POST'])
def select_mission():
    """
    Gestisce la selezione di una missione da parte dell'utente.
    Se l'utente seleziona una missione, la salva nella sessione e reindirizza
    alla pagina di visualizzazione della missione.
    Se non ci sono missioni disponibili, mostra un messaggio di errore.
    Se non è stata selezionata alcuna missione, mostra un messaggio di avviso.
    Se non esiste un gestore di missioni nella sessione, ne crea uno nuovo e
    lo salva nella sessione.
    Seleziona una missione dalla lista delle missioni disponibili e la salva
    nella sessione.
    Dalla missione selezionata, salva anche l'ambiente associato nella
    sessione.

    Returns:
        Renderizza il template 'select_mission.html' con la lista delle
        missioni disponibili.
        Se una missione è stata selezionata, reindirizza alla pagina di
        visualizzazione della missione.
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
    descrizione_ambiente = descrizione()
    return render_template(
        'show_mission.html',
        missione=missione,
        ambiente=ambiente,
        premi_raggruppati=premi_raggruppati,
        descrizione_ambiente=descrizione_ambiente
    )


@staticmethod
def descrizione():
    """
    Il metodo descrive i cambiamenti
    che l'ambiente apporta ai personaggi e agli oggetti rispetto
    alle condizioni originali.

    Returns:
        dict: Un dizionario contenente i valori standard e le modifiche
              apportate dall'ambiente ai personaggi e agli oggetti.
    """
    from gioco.ambiente import Ambiente
    from gioco.classi import Mago, Ladro, Guerriero
    from gioco.oggetto import PozioneCura, Medaglione, BombaAcida
    from copy import deepcopy

    ambiente = session.get('ambiente')
    # print(f"DEBUG - ambiente: {ambiente}")
    if isinstance(ambiente, dict):
        ambiente = Ambiente.from_dict(ambiente)
    # print(f"DEBUG - ambiente: {ambiente}")

    # Dati base per classi derivate da personaggio
    # (definite in maniera statica per ridurre la complessità del metodo)
    classi_data = {
        'Guerriero': {'at_min': 15, 'att_max_bonus': 20, 'cura_base': 30},
        'Ladro': {'at_min': 5, 'att_max_bonus': 5, 'cura_base': 'da 10 a 40'},
        'Mago': {'at_min': -5, 'att_max_bonus': 10, 'cura_base': '20% della salute rimanente'}
    }

    # Importo dinamico delle classi
    classi_map = {'Mago': Mago, 'Ladro': Ladro, 'Guerriero': Guerriero}
    classi = {nome: classi_map[nome]("temp") for nome in classi_data.keys()}
    oggetti = [PozioneCura(), Medaglione(), BombaAcida()]

    # print(f"DEBUG - classi: {classi}")

    # valori standard
    val_standard = {}
    x ={}
    for nome, classe in classi.items():
        data = classi_data[nome]
        x[nome] = {
            'attacco': {
                'da': classe.attacco_min + data['at_min'],
                'a': classe.attacco_max + data['att_max_bonus']
            },
            'cura': {'recupero salute': str(data['cura_base'])}
        }
    val_standard['Chars'] = x

    # Aggiungo i valori degli oggetti al dizionario
    val_standard['Oggetto'] = {
        obj.__class__.__name__: {
            'valore': obj.valore,
            'tipo_oggetto': obj.tipo_oggetto
        } for obj in oggetti
    }

    # (la deepcopy è necessaria per non modificare val_standard)
    var_amb = deepcopy(val_standard)

    # Calcolo delle modifiche ambiente per i personaggi
    for nome, classe in classi.items():
        mod_att = int(ambiente.modifica_attacco(classe))
        mod_cura = int(ambiente.modifica_cura(classe))

        # print(f"DEBUG - {nome}: attacco={mod_att}, cura={mod_cura}")

        if mod_att != 0:
            if nome != 'Guerriero':
                var_amb['Chars'][nome]['attacco']['da'] += mod_att
            var_amb['Chars'][nome]['attacco']['a'] += mod_att

        if mod_cura != 0:
            segno = '+' if mod_cura > 0 else '-'
            cura_str = {
                'Mago': f"20% (salute rimanente {segno} {abs(mod_cura)})",
                'Ladro': f"da {10 + mod_cura} a {40 + mod_cura}",
                'Guerriero': f"{30 + mod_cura}"
            }
            var_amb['Chars'][nome]['cura']['recupero salute'] = cura_str[nome]

    # Modifica del campo valore degli oggetti
    for obj in oggetti:
        mod_obj = ambiente.modifica_effetto_oggetto(obj)
        if mod_obj != 0:
            var_amb['Oggetto'][obj.__class__.__name__]['valore'] += mod_obj

    # Debugging output
    print(f"val_standard: {val_standard}")
    print(f"var_amb: {var_amb}")

    return {'val_standard': val_standard, 'var_amb': var_amb}


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
