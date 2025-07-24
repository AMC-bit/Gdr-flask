from flask import redirect, render_template, session, url_for, request, flash, jsonify
import logging
import random
import os

from . import battle_bp
from gioco.oggetto import Oggetto
from gioco.ambiente import Ambiente
from gioco.missione import Missione
from gioco.strategy import Strategia
from gioco.inventario import Inventario
from gioco.personaggio import Personaggio
from gioco.schemas.missione import MissioniSchema
from gioco.schemas.inventario import InventarioSchema
from gioco.schemas.personaggio import PersonaggioSchema
from gioco.schemas.helper import get_all_subclasses
from characters.routes import load_char, get_owned_chars
from config import DATA_DIR_SAVE, DATA_DIR_INV, DATA_DIR_PGS
from utils.salvataggio import Json
from gioco.schemas.oggetto import get_all_subclasses
from config import DATA_DIR_SAVE, DATA_DIR_INV
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

def bold(txt):
        return f"<b>{txt}</b>"

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

        """
        # inserisco l'id nella sessione
        session['personaggi_selezionati'] = [
            pg['id'] for pg in personaggi_selezionati]
        print("Personaggi selezionati", session['personaggi_selezionati'])
        """

        # reindirizzo verso la pagina di destinazione
        return redirect(url_for('battle.auto_battle'))
    return render_template(
        'select_char.html',
        personaggi=pg_list,
        missione_corrente=missione_corrente
        )


def setup_battle():
    """Fa il setup dei dati prendendoli dai file json data/ save, inventari, personaggi
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

    # Deserializzazione oggetti
    missione_obj = MissioniSchema().load(missione)
    personaggio_schema = PersonaggioSchema(many=True)
    personaggi_selezionati_obj = personaggio_schema.load(personaggi_selezionati)
    #print(f"PERSONAGGI_OBJ : {personaggi_selezionati_obj}")

    #Carico gli inventari dei personaggi:
    inventari_pg_obj = []
    inventario_schema = InventarioSchema()
    for pg in personaggi_selezionati_obj:
        if not pg.sconfitto():
            pg_inv_path = os.path.join(DATA_DIR_INV, f"{str(pg.id)}.json")
            inventario_pg = Json.carica_dati(pg_inv_path)
            inventario_pg_obj = inventario_schema.load(inventario_pg)
            inventari_pg_obj.append(inventario_pg_obj)

    return missione_obj, personaggi_selezionati_obj, inventari_pg_obj

def assegna_premi(missione : Missione, messaggi_battaglia : list[str], personaggi_selezionati : list[Personaggio]  ,inventari : list[Inventario]):
    """Da chiamare a fine scontro in caso di vittoria per assegnare 
    i premi della missione agli inventari dei personaggi

    Args:
        missione (Missione): La missione corrente
        inventari (list[Inventario]): Inventari dei personaggi giocanti

    Returns:
        None
    """
    for inventario in inventari:
        print(f"INVENTARIO:{inventari}")
        for pg in personaggi_selezionati:
            print(f"PG:{pg}")
            if inventario.id_proprietario == pg.id:
                for premio in missione.premi:
                    print(f"PREMIO:{premio}")
                    #QUESTA è una PORCATA , cè da rimettere mano nella lista premi di ogni missione
                    oggetti_map = {
                    subcls.__name__: subcls
                    for subcls in get_all_subclasses(Oggetto)
                    }
                    oggetto_cls = oggetti_map[premio.classe]
                    nuova_istanza = oggetto_cls()
                    messaggi_battaglia.append(f"{bold(pg.nome)} ha ricevuto in premio {bold(nuova_istanza.nome)}")
                    inventario.aggiungi_oggetto(nuova_istanza)

@battle_bp.route('/auto_battle', methods=['GET'])
def auto_battle():
    if os.path.exists(path_save):
        # --- SETUP DATI ---
        setup = setup_battle()
        missione_obj = setup[0]
        personaggi_selezionati_obj = setup[1]
        nemici_obj = setup[0].nemici
        ambiente_obj = setup[0].ambiente
        inventari_pg = setup[2]
        inventari = []
        inventari += setup[2]
        inventari += missione_obj.inventari_nemici
        save_data = Json.carica_dati(path_save)
        tutti_personaggi = personaggi_selezionati_obj + nemici_obj

        # Inizializza messaggi e ordine turni se non presenti
        if 'ordine_turni' not in save_data:
            ordine_turni = ordine_iniziativa(tutti_personaggi)
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

        if not battaglia_finita:
            save_data['turno'] += 1
            save_data['ordine_turni'] = ordine_turni
            if indice_turno >= len(ordine_turni):
                indice_turno = 0
                save_data['indice_turno_corrente'] = indice_turno

            # ----- SEPARATORE DI TURNO -----
            save_data['messaggi_battaglia'].append(
                f"<hr><div class='text-center text-primary fw-bold my-2'>------- TURNO {save_data['turno']} -------</div>"
            )

            personaggio_turno_corrente = None
            for p in tutti_personaggi:
                if str(p.id) == ordine_turni[indice_turno] and not p.sconfitto():
                    personaggio_turno_corrente = p
                    break

            if not personaggio_turno_corrente:
                # Nessun personaggio disponibile, skip turno
                save_data['indice_turno_corrente'] = (indice_turno + 1) % len(ordine_turni)
                Json.scrivi_dati(path_save, save_data)
                return redirect(url_for('battle.auto_battle'))

            save_data['messaggi_battaglia'].append(
                f"È il turno di {bold(personaggio_turno_corrente.nome)}"
            )

            # Uso dell'inventario in maniera automatica
            inventario = None
            for inv in inventari:
                if (
                    isinstance(inv, Inventario)
                    and inv.id_proprietario == personaggio_turno_corrente.id
                ):
                    inventario = inv
                    break

            result = usa_inventario_automatico(
                inventario,
                personaggio_turno_corrente,
                missione_obj,
                (nemici_obj + personaggi_selezionati_obj)
            )
            txt = result[1]
            if txt:
                save_data['messaggi_battaglia'].append(txt)

            if personaggio_turno_corrente.npc:
                bersagli_validi = [p for p in personaggi_selezionati_obj if not p.sconfitto()]
            else:
                bersagli_validi = [n for n in nemici_obj if not n.sconfitto()]

            if bersagli_validi:
                bersaglio = random.choice(bersagli_validi)
                danno, msg = personaggio_turno_corrente.attacca(ambiente_obj.mod_attacco)
                if danno > 0:
                    msg = (
                        f"{bold(personaggio_turno_corrente.nome)} attacca "
                        f"{bold(bersaglio.nome)} per "
                        f"<span class='text-danger fw-bold'>{danno}</span> danni!"
                    )
                elif danno == 0:
                    msg = (
                        f"{bold(personaggio_turno_corrente.nome)} attacca "
                        f"{bold(bersaglio.nome)} ma non infligge danni!"
                    )
                else:
                    msg = (
                        f"{bold(personaggio_turno_corrente.nome)} tenta di attaccare "
                        f"{bold(bersaglio.nome)} ma fallisce!"
                    )

                bersaglio.subisci_danno(danno)
                save_data['messaggi_battaglia'].append(msg)

                if bersaglio.sconfitto():
                    ordine_turni.remove(str(bersaglio.id))
                    save_data['messaggi_battaglia'].append(
                        f"{bold(bersaglio.nome)} è stato <span class='text-danger fw-bold'>sconfitto!</span>"
                    )

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
                save_data['messaggi_battaglia'].append(
                    "<span class='text-danger fw-bold'>Tutti i personaggi sono stati sconfitti!</span>"
                )
            elif not npc_vivi:
                battaglia_finita = True
                vittoria = True
                assegna_premi(missione_obj, save_data['messaggi_battaglia'], personaggi_selezionati_obj, inventari_pg)
                save_data['messaggi_battaglia'].append(
                    "<span class='text-success fw-bold'>Tutti i nemici sono stati sconfitti! Vittoria!</span>"
                )

        # Salva stato, aggiorna file
        for pg in personaggi_selezionati_obj:
            file_name = f"{pg.id}.json"
            pg_path = os.path.join(DATA_DIR_PGS, file_name)
            inv_path = os.path.join(DATA_DIR_INV, file_name)
            if pg.sconfitto():
                if os.path.exists(pg_path):
                    os.remove(pg_path)
                if os.path.exists(inv_path):
                    os.remove(inv_path)
            else:
                Json.scrivi_dati(pg_path, PersonaggioSchema().dump(pg))
                for inv in inventari_pg:
                    if isinstance(inv, Inventario) and inv.id_proprietario == pg.id:
                        inventario = inv
                        Json.scrivi_dati(inv_path, InventarioSchema().dump(inventario))

        save_data['missione'] = MissioniSchema().dump(missione_obj)
        Json.scrivi_dati(path_save, save_data)

        if battaglia_finita is True:
            os.remove(path_save)

    else:
        flash('Non esiste il file di salvataggio', 'danger')
        return redirect(url_for('mission.select_mission'))

    return render_template(
        'auto_battle.html',
        battaglia_finita=battaglia_finita,
        vittoria=vittoria,
        messaggi=save_data['messaggi_battaglia'],
        personaggi=personaggi_selezionati_obj,
        nemici=nemici_obj,
        missione=missione_obj
    )


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
            txt = (f"{bold(pg.nome)} usa Bomba Acida su {bold(bersaglio.nome)} "
                f"infliggendo {-value} HP di danno")
            bersaglio.salute += value
        if value > 0:
            bersaglio = None
            txt = (f"{bold(pg.nome)} usa Pozione Curativa su se stesso "
                f"recuperando{value} HP")
            pg.salute += value
            if pg.salute >= pg.salute_max:
                pg.salute = pg.salute_max
                txt += ", che torna al massimo della salute."
            else:
                txt += f", recuperando {value} HP."
        logger.info(txt)
        return value, txt
    if inventario is None:
        txt = f"{bold(pg.nome)} non ha un inventario! Errore!!!!."
    elif inventario.oggetti is None:
        txt = f"{bold(pg.nome)} non ha oggetti nell'inventario."
    else:
        txt = f"{bold(pg.nome)} non utilizza oggetti in questo turno"
    return None, txt



        
# in ingresso lista di tutti i personaggi, e  sommo iniziativa + d20, ordino in base a qst, mettendo gli id
def ordine_iniziativa(tutti_personaggi):
    """
    Calcola l'iniziativa per ogni personaggio sommando il valore di iniziativa al tiro di un d20.
    Ritorna una lista ordinata di ID in base all'iniziativa decrescente.
    
    Args:
        personaggi (list): Lista di oggetti `Personaggio`.

    Returns:
        list: Lista ordinata di ID in base al punteggio iniziativa.
    """
    iniziativa = []
    for pg in tutti_personaggi:
        tiro = random.randint(1, 20)
        iniziativa.append((pg.id, pg.iniziativa + tiro))
    # Ordino per l'elemento 1 della tupla decrescente
    iniziativa.sort(key=lambda tuple: tuple[1], reverse=True)

    lista_ordinata_id = []
    for tupla in iniziativa:
        id = tupla[0]
        lista_ordinata_id.append(str(id))
    return lista_ordinata_id



@battle_bp.route('/TEMPLATE', methods=['GET', 'POST'])
def test_battle_v2():
    return render_template("TEMPLATE.html")