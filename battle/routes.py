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
from config import DATA_DIR_SAVE, DATA_DIR_INV
import time
path_save = os.path.join(
    DATA_DIR_SAVE, "salvataggio.json"
)

classi = {cls.__name__: cls for cls in Personaggio.__subclasses__()}
schema = PersonaggioSchema()
schema_inv = InventarioSchema()


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








@battle_bp.route('/test_battle', methods=['GET', 'POST'])
def test_battle():
    setup = setup_battle()
    missione = setup[0]
    personaggi = setup[1]
    inventari = setup [2]

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