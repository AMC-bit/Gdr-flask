import logging
import json
import os
from copy import deepcopy
from collections import defaultdict

from . import mission_bp

from gioco.oggetto import Oggetto
from gioco.personaggio import Personaggio
from gioco.ambiente import AmbienteSchema, Ambiente
from gioco.missione import GestoreMissioni, Missione
from gioco.schemas.missione import GestoreMissioniSchema, MissioniSchema
from flask import flash, render_template, request, session, \
    redirect, url_for

# richiedere a utente: nome, tipo ambiente, lista nemici, lista premi,
# strategia.

path_missioni = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'data', 'missioni_custom.json'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@mission_bp.route('/create_mission', methods=['GET', 'POST'])
def create_mission():
    if request.method == 'POST':
        nome = request.form.get('nome')
        tipo_ambiente = request.form.get('ambiente')
        strategia = request.form.get('strategia_nemici')

        nemici_input = request.form.get('nemici', '')
        premi_input = request.form.get('premi', '')

        lista_nemici = []
        for riga in nemici_input.strip().split('\n'):
            try:
                (
                    nome,
                    salute,
                    salute_max,
                    attacco_min,
                    attacco_max,
                    destrezza
                ) = riga.strip().split(':')
                nemico = Personaggio(
                    nome.strip(),
                    int(salute),
                    int(salute_max),
                    int(destrezza),
                    int(attacco_min),
                    int(attacco_max)
                )
                lista_nemici.append(nemico)
            except ValueError:
                flash(f"Errore nella riga nemico: {riga}", 'error')

        lista_premi = []
        for riga in premi_input.strip().split('\n'):
            try:
                nome, valore, classe, tipo_oggetto = riga.strip().split(':')
                premio = Oggetto(
                    nome.strip(),
                    classe.strip(),
                    int(valore),
                    tipo_oggetto.strip()
                )
                lista_premi.append(premio)
            except ValueError:
                flash(f"Errore nella riga premio: {riga}", 'error')

        ambiente = Ambiente(nome=tipo_ambiente)
        missione = Missione(
            nome=nome,
            ambiente=ambiente,
            nemici=lista_nemici,
            premi=lista_premi,
            strategia_nemici=strategia
        )

        missioni = []
        if os.path.exists(path_missioni):
            with open(path_missioni, 'r') as f:
                missioni = json.load(f)

        missioni.append(missione.to_dict())

        with open(path_missioni, 'w') as f:
            json.dump(missioni, f, indent=4)

        flash(f"Missione '{nome}' salvata con successo!", 'success')
        logger.info(f"Missione personalizzata creata: {nome}")
        return redirect(url_for('mission.select_mission'))

    return render_template('create_mission.html')


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
    schema = MissioniSchema()
    if request.method == 'POST':
        missione_id = request.form.get('missione_id')

        # Ricostruisce il gestore dalla sessione (stesso usato per GET)
        gestore_data = session.get('gestore_missioni')
        if gestore_data:
            gestore = GestoreMissioniSchema().load(gestore_data)
        else:
            # Fallback se la sessione è vuota
            gestore = GestoreMissioniSchema().prendi_Missione_Da_Json()
            session['gestore_missioni'] = GestoreMissioniSchema().dump(gestore)

        # Debug: stampa il missione_id ricevuto
        msg = f"DEBUG: missione_id ricevuto: '{missione_id}'"
        flash(msg, 'info')
        logger.info(msg)

        # Trova la missione con l'ID specificato
        missione_selezionata = None
        for missione in gestore.lista_missioni:
            msg = f"DEBUG: Confronto '{str(missione.id)}' con '{missione_id}'"
            flash(msg, 'info')
            logger.debug(msg)
            if str(missione.id) == missione_id:
                missione_selezionata = missione
                break

        if missione_selezionata:
            # Salva missione e ambiente in sessione
            session['missione'] = schema.dump(missione_selezionata)
            session['ambiente'] = AmbienteSchema().dump(
                missione_selezionata.ambiente
            )

            msg = f"Missione selezionata: {missione_selezionata.nome}"
            flash(msg, 'success')
            logger.info(msg)
            return redirect(url_for('mission.show_mission'))
        else:
            msg = 'Missione non trovata.'
            flash(msg, 'error')
            logger.info(msg)

    # GET: mostra il form di selezione
    if 'gestore_missioni' not in session:
        gestore = GestoreMissioniSchema().prendi_Missione_Da_Json()
        # Salva il gestore in sessione per mantenerlo coerente
        session['gestore_missioni'] = GestoreMissioniSchema().dump(gestore)
    else:
        # Ricostruisce il gestore dalla sessione
        gestore = GestoreMissioniSchema().load(session['gestore_missioni'])

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
        logger.error(msg)
        return redirect(url_for('mission.select_mission'))

    # Ricostruisce gli oggetti dai dati in sessione

    missione = MissioniSchema().load(missione_data)
    if not isinstance(missione, Missione):
        msg = 'Dati della missione non validi.'
        logger.error(msg)
        return redirect(url_for('mission.select_mission'))
    ambiente = missione.ambiente
    premi = missione.premi
    premi_raggruppati = defaultdict(list)
    for premio in premi:
        premi_raggruppati[premio.nome].append(premio)

    msg = f"Missione mostrata: {missione.nome}"
    flash(msg, 'info')

    logger.info(msg)
    descrizione_ambiente = description()

    return render_template(
        'show_mission.html',
        missione=missione,
        ambiente=ambiente,
        premi_raggruppati=premi_raggruppati,
        descrizione_ambiente=descrizione_ambiente
    )


# metodo per la ricerca dinamica delle sottoclassi di una classe specifica
def get_all_subclasses(cls, ricorsiva: bool = True):
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        if ricorsiva:
            all_subclasses.extend(get_all_subclasses(subclass))
    return all_subclasses


@staticmethod
def description():
    """
    Il metodo descrive i cambiamenti
    che l'ambiente apporta ai personaggi e agli oggetti rispetto
    alle condizioni originali.

    Returns:
        dict: Un dizionario contenente i valori standard e le modifiche
        apportate dall'ambiente ai personaggi e agli oggetti.
    """
    ambiente = None
    s_ambiente = session.get('ambiente')
    if isinstance(s_ambiente, dict):
        ambiente = AmbienteSchema().load(s_ambiente)

    # Dati base per classi derivate da personaggio
    # (definite in maniera statica per ridurre la complessità del metodo
    # a causa del sistema di cura_base)
    classi_data = {
        'Guerriero': {'cura_base': 30},
        'Ladro': {'cura_base': 'da 10 a 40'},
        'Mago': {'cura_base': '20% della salute rimanente'}
    }

    # Importo dinamico delle classi
    # Ottieni dinamicamente tutte le sottoclassi di Personaggio

    # Crea il mapping dinamico delle classi
    classi_map = {cls.__name__: cls for cls in get_all_subclasses(Personaggio)}
    classi = {nome: classi_map[nome]("temp") for nome in classi_data.keys()}
    oggetti = [cls for cls in get_all_subclasses(Oggetto)]

    # print(f"DEBUG - classi: {classi}")

    # valori standard
    val_standard = {}
    x = {}
    for nome, classe in classi.items():
        data = classi_data[nome]
        x[nome] = {
            'attacco': {
                'da': classe.attacco_min,
                'a': classe.attacco_max
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
    # print(f"val_standard: {val_standard}")
    # print(f"var_amb: {var_amb}")

    return {'val_standard': val_standard, 'var_amb': var_amb}


@mission_bp.route('/missioni')
def mostra_missioni():
    missioni = GestoreMissioni.lista_missioni
    return render_template('missioni.html', missioni=missioni)


@mission_bp.route('/missione/attiva')
def missione_attiva():
    missione = GestoreMissioni.sorteggia()
    if missione:
        missione.attiva = True
        session['missione'] = MissioniSchema().dump(missione)
        msg = f"Missione attiva: {missione.nome}, ID: {missione.id}"
        logger.info(msg)
        return render_template('missione_attiva.html', missione=missione)
    logger.info("Nessuna missione attiva al momento.")
    flash("Non ci sono missioni attive o disponibili.", 'warning')
    return redirect(url_for('mission.select_mission'))


@mission_bp.route('/missioni/stato')
def state_mission():
    gestore = GestoreMissioni()
    complete = gestore.finita()
    if complete:
        msg = "Tutte le missioni sono state completate."
        logger.info(msg)
    else:
        msg = "Ci sono missioni ancora da completare."
        logger.info(msg)
