import logging
import json
import os
from copy import deepcopy
from collections import defaultdict
from flask import flash, render_template, request, session, redirect, url_for
from utils.salvataggio import Json
from . import mission_bp
import config
from gioco.oggetto import Oggetto
from gioco.personaggio import Personaggio
from gioco.ambiente import Ambiente
from gioco.missione import Missione
from gioco.schemas.missione import MissioniSchema
from config import DATA_DIR_SAVE
from flask_login import login_required

path_missioni = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'data', 'missioni_custom.json'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

path_save = os.path.join(
    DATA_DIR_SAVE, "salvataggio.json"
)


def prendi_Missione_Da_Json():
    """Scansiona la dir missions, legge i file json all'interno, usa lo schema
    si missioni, e ritorna la lista di missioni presenti.

    Returns:
        list: lista di dizionari, ogni dizionario è una missione serializzata
    """
    lista = []
    schema = MissioniSchema()
    routes = config.DATA_DIR_MIS
    for files in os.listdir(routes):
        if files.endswith(".json"):
            with open(os.path.join(routes, files), 'r') as file:
                data = json.load(file)
                missione = schema.load(data)
                lista.append(missione)
    return lista


@mission_bp.route('/select_mission', methods=['GET', 'POST'])
@login_required
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
    # Recupero dal json Static\json\missions tutte le missioni
    missioni = prendi_Missione_Da_Json()
    # Se c'è già una missione in sessione, la passo all'Html per presettare il form

    # Recupero dal form post l'id della missione selezionata
    if request.method == 'POST':
        missione_id = request.form.get('missione_id')

        # Debug: stampa il missione_id ricevuto
        msg = f"DEBUG: missione_id ricevuto: {missione_id}"
        logger.info(msg)

        # Trova la missione con l'ID selezionato nel form
        missione_selezionata = None
        for missione in missioni:
            msg = (
                f"DEBUG: Confronto {missione.id} "
                f"Tipo: {type(missione.id)} con {missione_id} "
                f"Tipo: {type(missione_id)}"
            )
            logger.debug(msg)
            if str(missione.id) == missione_id:
                missione_selezionata = missione
                break

        if missione_selezionata:
            # Salva missione e ambiente in sessione
            if  not missione_selezionata.completata:
                #Qua non ci sarebbe da porre la missione come attiva ?
                missione = {"missione": MissioniSchema().dump(missione_selezionata)}
                Json.scrivi_dati(path_save, missione)

            msg = f"Missione selezionata: {missione_selezionata.nome}"
            logger.info(msg)
            return redirect(url_for('mission.show_mission'))
        else:
            msg = 'Missione non trovata.'
            flash(msg, 'danger')
            logger.info(msg)
    return render_template('select_mission.html', missioni = missioni )


@mission_bp.route('/show_mission')
@login_required
def show_mission():
    """
    Mostra i dettagli della missione selezionata.
    Se non è stata selezionata alcuna missione, mostra un messaggio di errore.
    """
    data = Json.carica_dati(path_save)
    missione_data = data.get('missione')

    if not missione_data:
        msg = 'Nessuna missione selezionata.'
        flash(msg, 'danger')
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

    logger.info(msg)
    descrizione_ambiente = description(ambiente)

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
def description(ambiente: Ambiente = None):
    """
    Il metodo descrive i cambiamenti
    che l'ambiente apporta ai personaggi e agli oggetti rispetto
    alle condizioni originali.

    Returns:
        dict: Un dizionario contenente i valori standard e le modifiche
        apportate dall'ambiente ai personaggi e agli oggetti.
    """

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
    oggetti = [cls() for cls in get_all_subclasses(Oggetto)]

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
    # print(f"val_standard: {val_standard}"
    # f"\nvar_amb: {var_amb}")

    return {'val_standard': val_standard, 'var_amb': var_amb}


@mission_bp.route('/missione/attiva')
def missione_attiva():
        # Controlla se esiste già una missione attiva in sessione
    missione_sessione = session.get('missione')
    if missione_sessione:
        return render_template('missione_attiva.html', missione=missione_sessione)

    missioni = session.get('missioni', [])

    # Cerca una missione attiva
    for missione in missioni:
        if missione.get('attiva') and not missione.get('completata'):
            session['missione'] = missione
            return render_template('missione_attiva.html', missione=missione)

    # Se non ci sono missioni attive, reindirizza alla selezione
    msg = "Nessuna missione attiva disponibile."
    logger.info(msg)
    flash(msg, 'warning')
    return redirect(url_for('mission.select_mission'))
