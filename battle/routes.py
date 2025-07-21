from flask import redirect, render_template, session, url_for, request, flash, jsonify
from . import battle_bp
import os
import logging
from gioco.personaggio import Personaggio
from gioco.inventario import Inventario
from gioco.ambiente import Ambiente
from gioco.missione import Missione
from utils.salvataggio import Json
from characters.routes import load_char, get_owned_chars
from gioco.schemas.personaggio import PersonaggioSchema
from gioco.schemas.inventario import InventarioSchema
from gioco.schemas.ambiente import AmbienteSchema
from gioco.schemas.missione import MissioniSchema
from inventory.routes import carica_inventario_da_json
from utils.salvataggio import Json
import random
import json
from config import DATA_DIR_SAVE, DATA_DIR_INV, DATA_DIR_MIS

path_save = os.path.join(
    DATA_DIR_SAVE, "salvataggio.json"
)
path_inv = os.path.join(
    DATA_DIR_INV, "inventario.json"
)

classi = {cls.__name__: cls for cls in Personaggio.__subclasses__()}
schema = PersonaggioSchema()
schema_inv = InventarioSchema()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@battle_bp.route('/select_char', methods=['GET', 'POST'])
def select_char():
    # if request.method == 'POST':
    # prendo i dati da sessione:

    missione_corrente = Json.carica_dati(path_save)['missione']

    pg_id_list = load_char()
    pg_list = get_owned_chars(pg_id_list)
    if request.method == 'POST':
        # Request.form.getlist restituisce una lista di stringhe
        indici_selezionati = request.form.getlist('selected_chars')
        personaggi_selezionati = []
        # se nel form passi l'indice iallora dobbiamo ricreare il personaggio per conservare i dati in sessione
        for idx in indici_selezionati:
            try:
                # creazione oggetti
                for pgs in pg_list:
                    if idx == pgs['id']:
                        pg = schema.dump(pgs)
                personaggi_selezionati.append(pg)
            except (ValueError, IndexError):
                continue

        data_load = Json.carica_dati(path_save)
        if isinstance(data_load, dict):
            data_load['personaggi_selezionati'] = personaggi_selezionati
        else:
            msg = 'Dati non in formato corretto'
            flash(msg, 'danger')
        Json.scrivi_dati(path_save, data_load)

        # inserisco l'id nella sessione
        session['personaggi_selezionati'] = [
            pg['id'] for pg in personaggi_selezionati]
        print("Personaggi selezionati", session['personaggi_selezionati'])
        # reindirizzo verso la pagina di destinazione
        return redirect(url_for('battle.test_battle'))
    return render_template(
        'select_char.html',
        personaggi=pg_list,
        missione_corrente=missione_corrente
        )

def setup_battle():
    """TODO Fa il setup dei dati prendendoli dai file json data/ save, inventari, personaggi
    Deserializza i dati dai json e ritorna gli oggetti

    Returns:
        Missione: La missione deserializzata con dentro i suoi campi la lista dei
        nemici, l'ambiente, la lista degli inventari dei nemici e la lista dei premi.

        List[Personaggio]: La lista dei personaggi selezionati dei giocatori.

        List[Inventario]: La lista degli inventari dei giocatori.
    """
    # --- SETUP DATI ---
    # Recupera o crea la lista unica di personaggi (giocatori + npc)
    save_data = Json.carica_dati(path_save)
    missione = save_data['missione']
    #print(f"MISSIONE DICT :{missione}")
    personaggi_selezionati = Json.carica_dati(path_save)['personaggi_selezionati']
    #print(f"PERSONAGGI SELEZIONATI DICT :{personaggi_selezionati}")
    #nemici = missione['nemici']
    #ambiente = missione['ambiente']
    #inventari_nemici = missione['inventari_nemici']

    #deserializzo i dati recuperati da json
    missione_obj = MissioniSchema().load(missione)
    personaggio_schema = PersonaggioSchema(many=True)
    personaggi_selezionati_obj = personaggio_schema.load(personaggi_selezionati)
    #print(f"PERSONAGGI_OBJ : {personaggi_selezionati_obj}")
    #nemici_obj = personaggio_schema.load(nemici)
    #ambiente_obj = AmbienteSchema().load(ambiente)
    #inventari_nemici_obj = InventarioSchema(many=True).load(inventari_nemici)

    #tutti_personaggi_obj = personaggi_selezionati_obj + nemici_obj

    #Carico gli inventari dei personaggi:
    inventari_pg_obj = []
    inventario_schema = InventarioSchema()
    for pg in personaggi_selezionati_obj:
        pg_inv_path = os.path.join(DATA_DIR_INV, f"{str(pg.id)}.json")
        inventario_pg = Json.carica_dati(pg_inv_path)
        inventario_pg_obj = inventario_schema.load(inventario_pg)
        inventari_pg_obj.append(inventario_pg_obj)

    return missione_obj, personaggi_selezionati_obj, inventari_pg_obj


@battle_bp.route('/test_battle', methods=['GET', 'POST'])
def test_battle():
    setup = setup_battle()
    missione = setup[0]
    personaggi = setup[1]
    inventari = setup [2]

    return render_template(
        'test_battle.html',
        pg = personaggi,
        missione = missione,
        inventari_pg = inventari
    )


@battle_bp.route('/TEMPLATE', methods=['GET', 'POST'])
def test_battle_v2():
    return render_template("TEMPLATE.html")


def carica_inventario(
    pg_turno_corrente: Personaggio,
    lista_inv_pc: list[Inventario],
    lista_inv_npc: list[Inventario]
    ) -> Inventario:
    """
    Carica l'inventario del personaggio corrente.

    Args:
        pg_turno_corrente (Personaggio): Il personaggio corrente.
        lista_inv_pc (list[Inventario]):
        L'elenco degli inventari dei personaggi giocanti.
        lista_inv_npc (list[Inventario]):
        L'elenco degli inventari dei personaggi non giocanti.

    Returns:
        Inventario: L'inventario del personaggio corrente, se trovato.
    """
    inventario = None
    if pg_turno_corrente.npc:
        # cerco l'inventario tra quelli NPC
        for inv in lista_inv_npc:
            if inv.id_proprietario == pg_turno_corrente.id:
                inventario = inv
                break
    else:
        # cerco l'inventario tra quelli PC
        for inv in lista_inv_pc:
            if inv.id_proprietario == pg_turno_corrente.id:
                inventario = inv
                break
    # controllo finale
    if inventario is None:
        logging.error(
            f"Inventario non trovato per il personaggio: "
            f"{pg_turno_corrente.nome}"
        )
        return None
    return inventario


def mostra_inventario(inventario: Inventario) -> jsonify:
    """
    Mostra il contenuto dell'inventario.

    Args:
        inventario (Inventario): L'inventario da mostrare.

    Returns:
        JSON: La lista degli oggetti presenti nell'inventario.
    """
    lista_oggetti = [
        {
            'nome': oggetto.nome
        } for oggetto in inventario.oggetti
    ]
    return jsonify(lista_oggetti)


def usa_inventario(
    inventario: Inventario,
    pg: Personaggio,
    ambiente: Ambiente,
    nome_oggetto: str,
    bersaglio: Personaggio = None
) -> tuple[int | None, str]:
    """
    Utilizza un oggetto dall'inventario.

    Args:
        inventario (Inventario): L'inventario da cui utilizzare l'oggetto.
        pg (Personaggio): Il personaggio che utilizza l'oggetto.
        ambiente (Ambiente): L'ambiente in cui si trova il personaggio.
        nome_oggetto (str): Il nome dell'oggetto da utilizzare.
        bersaglio (Personaggio, optional):
        Il bersaglio dell'effetto dell'oggetto. Defaults to None.

    Returns:
        tuple[int | None, str]:
        Il risultato dell'uso dell'oggetto e un messaggio descrittivo.
    """

    txt1 = f"{pg.nome} usa {nome_oggetto} su {bersaglio.nome}"

    # controllo se il bersaglio è specificato,
    # altrimenti usa il personaggio stesso
    if bersaglio is None:
        bersaglio = pg
        txt1 = f"{pg.nome} usa {nome_oggetto} su se stesso"

    # cerco il tipo di oggetto nell'inventario,
    # servirà per determinarne l'effetto
    tipo_oggetto = None
    for obj in inventario.oggetti:
        if obj.nome == nome_oggetto:
            tipo_oggetto = obj.tipo_oggetto
            break

    if tipo_oggetto is not None:
        risultato = inventario.usa_oggetto(nome_oggetto, ambiente)
        if tipo_oggetto == "Ristorativo":
            bersaglio.salute += risultato
            if bersaglio.salute > bersaglio.salute_max:
                bersaglio.salute = bersaglio.salute_max
                txt = f"{txt1}, che torna al massimo della salute."
            else:
                txt = f"{txt1}, recuperando {risultato} HP."
        elif tipo_oggetto == "Offensivo":
            risultato = risultato # Il danno è negativo per l'oggetto offensivo
            bersaglio.salute += risultato
            txt = f"{txt1}, infliggendo {-risultato} HP di danno."
        elif tipo_oggetto == "Buff":
            bersaglio.attacco_max += risultato
            txt = f"{txt1}, incrementando l'attacco massimo di {risultato}."
        else:
            txt = f"{txt1}, ma non ha effetto."
    else:
        txt = f"{pg.nome} non ha l'oggetto {nome_oggetto} nell'inventario."
    logger.info(txt)
    return risultato, txt
