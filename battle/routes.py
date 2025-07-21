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
            flash(msg, 'error')
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


@battle_bp.route('/test_battle', methods=['GET', 'POST'])
def test_battle():
    # --- SETUP DATI ---
    # Recupera o crea la lista unica di personaggi (giocatori + npc)
    save_data = Json.carica_dati(path_save)
    missione = save_data['missione']
    #print(f"MISSIONE DICT :{missione}")
    personaggi_selezionati = Json.carica_dati(path_save)['personaggi_selezionati']
    #print(f"PERSONAGGI SELEZIONATI DICT :{personaggi_selezionati}")
    nemici = missione['nemici']
    ambiente = missione['ambiente']

    #deserializzo i dati recuperati da json
    missione_obj = MissioniSchema().load(missione)
    personaggio_schema = PersonaggioSchema(many=True)
    personaggi_selezionati_obj = personaggio_schema.load(personaggi_selezionati)
    #print(f"PERSONAGGI_OBJ : {personaggi_selezionati_obj}")
    nemici_obj = personaggio_schema.load(nemici)
    ambiente_obj = AmbienteSchema().load(ambiente)
    tutti_personaggi = personaggi_selezionati_obj + nemici_obj

    #Carico gli inventari dei personaggi:
    inventari_pg_obj = []
    inventario_schema = InventarioSchema()
    for pg in personaggi_selezionati_obj:
        pg_inv_path = os.path.join(DATA_DIR_INV, f"{str(pg.id)}.json")
        inventario_pg = Json.carica_dati(pg_inv_path)
        inventario_pg_obj = inventario_schema.load(inventario_pg)
        inventari_pg_obj.append(inventario_pg_obj)

    # Generiamo una lista con l'ordine in iniziativa dei pg
    if save_data:
        if 'ordine_turni' not in save_data :
            ordine_turni = list(range(len(tutti_personaggi)))
            random.shuffle(ordine_turni)
            save_data['ordine_turni'] = ordine_turni
            #ricarichiamo sul jason la versione aggiornata di save_data dopo 
            #ogni nuovo ingresso o modifica
            Json.scrivi_dati(path_save, save_data)

        if 'indice_turno_corrente' not in save_data:
            save_data['indice_turno_corrente'] = 0
            Json.scrivi_dati(path_save, save_data)

        if 'messaggi_battaglia' not in save_data:
            save_data['messaggi_battaglia'] = []
            Json.scrivi_dati(path_save, save_data)
    # TODO Ricordati di cancellare i messaggi battaglia a fine battaglia


    # --- TURNO CORRENTE ---
    ordine_turni = save_data['ordine_turni']
    indice_turno = save_data['indice_turno_corrente']
    idx_pg = ordine_turni[indice_turno]
    personaggio_turno_corrente = tutti_personaggi[idx_pg]

    # --- CONDIZIONI DI VITTORIA/SCONFITTA ---
    pc_vivi = [p for p in personaggi_selezionati_obj if not p.sconfitto()]
    npc_vivi = [p for p in nemici_obj if not p.sconfitto()]
    battaglia_finita = False
    vittoria = False
    if not pc_vivi:
        battaglia_finita = True
        vittoria = False
        save_data['messaggi_battaglia'].append(
            "Tutti i personaggi sono stati sconfitti! Sconfitta!")
        Json.scrivi_dati(path_save, save_data)
    elif not npc_vivi:
        battaglia_finita = True
        vittoria = True
        save_data['messaggi_battaglia'].append(
            "Tutti i nemici sono stati sconfitti! Vittoria!")
        Json.scrivi_dati(path_save, save_data)

    # --- AZIONI TURNO GIOCATORE ---
    #print(f"BATTAGLIA FINITA :{battaglia_finita}")
    if request.method == 'POST' and not battaglia_finita:
        azione = request.form.get('azione')
        bersaglio_id = request.form.get('bersaglio_id')
        oggetto_id = request.form.get('oggetto_id')

        # Trova bersaglio
        for p in tutti_personaggi:
            if str(p.id) == bersaglio_id and not p.sconfitto():
                save_data['messaggi_battaglia'].append(
                "SONO QUA 2!")
                Json.scrivi_dati(path_save, save_data)

                bersaglio = p
                if azione == 'attacco' and bersaglio:
                    danno = personaggio_turno_corrente.attacca()
                    bersaglio.subisci_danno(danno)
                    save_data['messaggi_battaglia'].append(f"{personaggio_turno_corrente.nome} attacca {bersaglio.nome} per {danno} danni!")
                    Json.scrivi_dati(path_save, save_data)
                    if bersaglio.sconfitto():
                        save_data['messaggi_battaglia'].append(f"{bersaglio.nome} è stato sconfitto!")

                elif azione == 'usa_oggetto' and bersaglio and oggetto_id:
                    inventario = None
                    for inv in inventari_pg_obj :
                        if inv.id_proprietario == personaggio_turno_corrente.id:
                            inventario = inv
                            break
                    oggetto = None
                    if inventario:
                        for o in inventario.oggetti :
                            if o.id == oggetto_id :
                                oggetto = o
                                break
                    if oggetto:
                        risultato = inventario.usa_oggetto(oggetto, ambiente_obj)
                        bersaglio.recupera_salute(risultato)
                        save_data['messaggi_battaglia'].append(f"{personaggio_turno_corrente.nome} usa {oggetto.nome} su {bersaglio.nome} per {risultato} HP!")

                    Json.scrivi_dati(path_save, save_data)
                    
    # Passa al prossimo turno vivo
    for _ in range(len(ordine_turni)):
        indice_turno = (indice_turno + 1) % len(ordine_turni)
        if not tutti_personaggi[ordine_turni[indice_turno]].sconfitto():
            break
        save_data['indice_turno_corrente'] = indice_turno
        Json.scrivi_dati(path_save, save_data)

        #Aggiorniamo missione
        save_data['missione'] = MissioniSchema().dump(missione_obj)
        Json.scrivi_dati(path_save, save_data)
        return redirect(url_for('battle.test_battle'))

    # --- AZIONE NPC ---
    if not battaglia_finita and personaggio_turno_corrente.npc:
        # Scegli un bersaglio valido (giocatore vivo)
        bersagli_validi = [p for p in personaggi_selezionati_obj if not p.sconfitto()]
        if bersagli_validi:
            bersaglio = random.choice(bersagli_validi)
            danno = personaggio_turno_corrente.attacca()
            bersaglio.subisci_danno(danno)
            save_data['messaggi_battaglia'].append(f"{personaggio_turno_corrente.nome} (NPC) attacca {bersaglio.nome} per {danno} danni!")
            if bersaglio.sconfitto():
                save_data['messaggi_battaglia'].append(f"{bersaglio.nome} è stato sconfitto!")
            Json.scrivi_dati(path_save, save_data)

        # Passa al prossimo turno vivo
        for _ in range(len(ordine_turni)):
            indice_turno = (indice_turno + 1) % len(ordine_turni)
            if not tutti_personaggi[ordine_turni[indice_turno]].sconfitto():
                break
        save_data['indice_turno_corrente'] = indice_turno
        #Aggiorniamo missione
        save_data['missione'] = MissioniSchema().dump(missione_obj)
        Json.scrivi_dati(path_save, save_data)
        return redirect(url_for('battle.test_battle'))

    # --- INVENTARIO DEL TURNO CORRENTE ---
    inventario_corrente = None
    for inv in inventari_pg_obj:
        #print(f"CONFRONTO {inv.id} TYPE :{type(inv.id)} CON {personaggio_turno_corrente.id} TYPE :{type(personaggio_turno_corrente.id)}")
        if inv.id_proprietario == personaggio_turno_corrente.id:
            inventario_corrente = inv
            break

    return render_template(
        'test_battle.html',
        tutti_personaggi = tutti_personaggi,
        ambiente = ambiente_obj,
        missione = missione_obj,
        personaggio_turno_corrente = personaggio_turno_corrente,
        inventario_corrente = inventario_corrente,
        battaglia_finita = battaglia_finita,
        vittoria = vittoria,
        messaggi = save_data['messaggi_battaglia']
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
