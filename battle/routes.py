from flask import redirect, render_template, session, url_for, request, flash, jsonify

from gioco.oggetto import Oggetto
from gioco.strategy import Strategia
from . import battle_bp
import os
import logging
import random
import json
import time
from gioco.personaggio import Personaggio
from gioco.classi import Mago, Ladro, Guerriero
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

@battle_bp.route('/show_inventory', methods=['GET', 'POST'])
def show_inventory():
    # recupero dalla sessione il personaggio che sta giocando il turno corrente
    if 'personaggio_turno_corrente' in session:
        personaggio_turno_corrente = session['personaggio_turno_corrente']
        cls_pg_turno_corr = classi.get(personaggio_turno_corrente.get('classe'))
        if cls_pg_turno_corr:
                personaggio_turno_corrente = cls_pg_turno_corr.from_dict(personaggio_turno_corrente)

        # recupero inventari dalla sessione cerco l'inventario del personaggio in turno e lo deserializzo
        inventari_des = []
        if 'inventari_selezionati' in session :
            inventari = session['inventari_selezionati']
            for inventario in inventari:
                if inventario['id_proprietario'] ==  personaggio_turno_corrente.id:
                    inventario = Inventario.from_dict(inventario)

    return render_template(
        'show_inventory.html',
        personaggio_turno_corrente=personaggio_turno_corrente,
        inventario=inventario)



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
        # se nel form passi l'indice allora dobbiamo ricreare il personaggio per conservare i dati in sessione
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
            flash(msg, 'error')
        # reset dei dati della battaglia per testing
        if "messaggi_battaglia" in data_load:
            # rimuove la chiave
            del data_load["messaggi_battaglia"]
        if "ordine_turni" in data_load:
            del data_load["ordine_turni"]
        if "indice_turno_corrente" in data_load:
            data_load["indice_turno_corrente"] = 0
        if "turno" in data_load:
            data_load["turno"] = 0
        Json.scrivi_dati(path_save, data_load)

        # inserisco l'id nella sessione
        session['personaggi_selezionati'] = [
            pg['id'] for pg in personaggi_selezionati]
        print("Personaggi selezionati", session['personaggi_selezionati'])
        # reindirizzo verso la pagina di destinazione
        return redirect(url_for('battle.auto_battle'))
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
    save_data = Json.carica_dati(path_save)
    missione = save_data['missione']
    #print(f"MISSIONE DICT :{missione}")
    personaggi_selezionati = Json.carica_dati(path_save)['personaggi_selezionati']
    #print(f"PERSONAGGI SELEZIONATI DICT :{personaggi_selezionati}")
    #nemici = missione['nemici']
    #ambiente = missione['ambiente']
    #inventari_nemici = missione['inventari_nemici']

    # Deserializzazione oggetti
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


@battle_bp.route('/auto_battle', methods=['GET'])
def auto_battle():
    # --- SETUP DATI ---
    setup = setup_battle()
    missione_obj = setup[0]
    personaggi_selezionati_obj = setup[1]
    nemici_obj = setup[0].nemici
    ambiente_obj = setup[0].ambiente
    save_data = Json.carica_dati(path_save)
    tutti_personaggi = personaggi_selezionati_obj + nemici_obj

    # Inizializza messaggi e ordine turni se non presenti

    if 'ordine_turni' not in save_data:
        ordine_turni = list(range(len(tutti_personaggi)))
        random.shuffle(ordine_turni)
        save_data['ordine_turni'] = ordine_turni
    if 'turno' not in save_data:
        save_data['turno'] = 0
    if 'indice_turno_corrente' not in save_data:
        save_data['indice_turno_corrente'] = 0

    if 'messaggi_battaglia' not in save_data:
        save_data['messaggi_battaglia'] = []

    ordine_turni = save_data['ordine_turni']
    indice_turno = save_data['indice_turno_corrente']
    battaglia_finita = False
    vittoria = False
    # --- Controlla se la battaglia è già finita ---
    pc_vivi = [p for p in personaggi_selezionati_obj if not p.sconfitto()]
    npc_vivi = [p for p in nemici_obj if not p.sconfitto()]
    if not pc_vivi:
        battaglia_finita = True
        vittoria = False
        save_data['messaggi_battaglia'].append("Tutti i personaggi sono stati sconfitti! Sconfitta!")
    elif not npc_vivi:
        battaglia_finita = True
        vittoria = True
        save_data['messaggi_battaglia'].append("Tutti i nemici sono stati sconfitti! Vittoria!")

    if not battaglia_finita:
        save_data['turno'] += 1
        ordine_turni = [idx for idx in ordine_turni if not tutti_personaggi[idx].sconfitto()]
        save_data['ordine_turni'] = ordine_turni
        if indice_turno >= len(ordine_turni):
            indice_turno = 0
            save_data['indice_turno_corrente'] = indice_turno
        personaggio_turno_corrente = tutti_personaggi[ordine_turni[indice_turno]]
        save_data['messaggi_battaglia'].append(
            f"Turno {save_data['turno']} - è il turno di {personaggio_turno_corrente.nome}!"
            )

        # setup per l'uso dell'inventario in maniera automatica
        pg = personaggio_turno_corrente
        inventari = []
        inventari.extend(setup[2])
        inventari.extend(missione_obj.inventari_nemici)
        inventario = None
        for inv in inventari:
            if isinstance(inv, Inventario) and inv.id_proprietario == pg.id:
                inventario = inv
                break

        result = usa_inventario_automatico(
            inventario,
            pg,
            missione_obj,
            (nemici_obj + personaggi_selezionati_obj)
            )
        txt = result[1]
        save_data['messaggi_battaglia'].append(txt)

        if personaggio_turno_corrente.npc:
            bersagli_validi = [p for p in personaggi_selezionati_obj if not p.sconfitto()]
        else:
            bersagli_validi = [n for n in nemici_obj if not n.sconfitto()]

        if bersagli_validi:
            bersaglio = random.choice(bersagli_validi)
            danno = personaggio_turno_corrente.attacca(ambiente_obj.mod_attacco)
            bersaglio.subisci_danno(danno)
            save_data['messaggi_battaglia'].append(
                f"{personaggio_turno_corrente.nome} attacca {bersaglio.nome} per {danno} danni!"
            )
            if bersaglio.sconfitto():
                save_data['messaggi_battaglia'].append(f"{bersaglio.nome} è stato sconfitto!")

        save_data['personaggi_selezionati'] = PersonaggioSchema(many=True).dump(personaggi_selezionati_obj)
        missione_obj.nemici = nemici_obj
        save_data['missione'] = MissioniSchema().dump(missione_obj)

        save_data['indice_turno_corrente'] = (indice_turno + 1) % len(ordine_turni)
        Json.scrivi_dati(path_save, save_data)
        pc_vivi = [p for p in personaggi_selezionati_obj if not p.sconfitto()]
        npc_vivi = [p for p in nemici_obj if not p.sconfitto()]
        if not pc_vivi:
            battaglia_finita = True
            vittoria = False
            save_data['messaggi_battaglia'].append("Tutti i personaggi sono stati sconfitti!")
        elif not npc_vivi:
            battaglia_finita = True
            vittoria = True
            save_data['messaggi_battaglia'].append("Tutti i nemici sono stati sconfitti! Vittoria!")

    # Salvataggio stato
    save_data['missione'] = MissioniSchema().dump(missione_obj)
    Json.scrivi_dati(path_save, save_data)
    # ripristino stato nemici solo per scopo di testing
    if battaglia_finita:
        for n in nemici_obj:
            n.salute = n.salute_max
            n.storico_danni_subiti = []
        missione_obj.nemici = nemici_obj
        save_data['missione'] = MissioniSchema().dump(missione_obj)
        Json.scrivi_dati(path_save, save_data)
    return render_template(
        'auto_battle.html',
        battaglia_finita=battaglia_finita,
        vittoria=vittoria,
        messaggi=save_data['messaggi_battaglia']
    )


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
            'nome': oggetto.nome,
        } for oggetto in inventario.mostra_lista_inventario()
        if isinstance(oggetto, Oggetto)
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


def usa_inventario_automatico(
    inventario: Inventario,
    pg: Personaggio,
    missione: Missione,
    bersagli: list[Personaggio],
    strategia: Strategia = None
) -> tuple[int | None, str]:
    """
    Utilizza un oggetto dall'inventario in modo automatico.

    Args:
        inventario (Inventario): L'inventario da cui utilizzare l'oggetto.
        pg (Personaggio): Il personaggio che utilizza l'oggetto.
        ambiente (Ambiente): L'ambiente in cui si trova il personaggio.
        bersagli (list[Personaggio]): I bersagli dell'effetto dell'oggetto.

    Returns:
        tuple[int | None, str]:
        Il risultato dell'uso dell'oggetto e un messaggio descrittivo.
    """
    ambiente = missione.ambiente

    if strategia is None:
        strategia = missione.strategia_nemici

    bersagli = [
        bersaglio for bersaglio in bersagli
        if bersaglio.salute > 0
        and bersaglio != pg
        and bersaglio.npc != pg.npc
    ]

    value = strategia.uso_inventario_npc(pg.salute, inventario, ambiente)

    if value is not None:
        if value < 0:
            # Se il valore è negativo, significa che l'oggetto è offensivo
            bersaglio = random.choice(bersagli)
            txt = (f"{pg.nome} usa Bomba Acida su {bersaglio.nome} "
                   f"infliggendo {-value} HP di danno")
            bersaglio.salute += value
        if value > 0:
            bersaglio = None
            txt = (f"{pg.nome} usa Pozione Curativa su se stesso "
                   f"recuperando {value} HP")
            pg.salute += value
            if pg.salute >= pg.salute_max:
                pg.salute = pg.salute_max
                txt += ", che torna al massimo della salute."
            else:
                txt += f", recuperando {value} HP."
        logger.info(txt)
        return value, txt
    if inventario is None:
        txt = f"{pg.nome} non ha un inventario! Errore!!!!."
    elif inventario.oggetti is None:
        txt = f"{pg.nome} non ha oggetti nell'inventario."
    else:
        txt = f"{pg.nome} non utilizza oggetti in questo turno"
    return None, txt
