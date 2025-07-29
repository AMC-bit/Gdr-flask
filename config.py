import os
import json
from auth.models import User

# cartella root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# directory file JSON dei personaggi
DATA_DIR_PGS = os.path.join(BASE_DIR, 'data', 'json', 'personaggi')

# directory file JSON degli inventari
DATA_DIR_INV = os.path.join(BASE_DIR, 'data', 'json', 'inventari')

# directory file JSON del salvataggio della battaglia
DATA_DIR_SAVE = os.path.join(BASE_DIR, 'data', 'json', 'save')

# directory file JSON delle missioni
DATA_DIR_MIS = os.path.join(BASE_DIR, 'static', 'json', 'missions')

# directory file JSON classifica
DATA_DIR_LEADERBOARD = os.path.join(BASE_DIR, 'data', 'json', 'leaderboard')

# file JSON con classifica
LEADERBOARD_FILE = os.path.join(DATA_DIR_LEADERBOARD, 'leaderboard.json')

# Numero di giocatori massimo per ogni singolo utente
NUMERO_MAX_PGS = 5


NUMERO_MAX_PGS = 5  # Numero massimo di personaggi che un utente può usare in una battaglia

def CreateDirs():
    """
    Crea directory per i file JSON necessarie allo svolgimento del gioco
    se non sono esistenti
    """
    for d in (
        DATA_DIR_PGS,
        DATA_DIR_INV,
        DATA_DIR_SAVE,
        DATA_DIR_MIS,
        DATA_DIR_LEADERBOARD
        ):
        os.makedirs(d, exist_ok=True)

        # crea file gitkeep se non esiste
        gitkeep = os.path.join(d, '.gitkeep')
        if not os.path.exists(gitkeep):
            open(gitkeep, 'a').close()


def add_user_leaderboard(user_id):
    """
    Funzione di aggiunta di un utente al file JSON della classifica
    """
    user_id = str(user_id)

    leaderboard = load_leaderboard()

    if user_id not in leaderboard:
        leaderboard[user_id] = {
            "nome": User.query.get(user_id).nome,
            "partite_giocate": 0,
            "partite_vinte": 0,
            "punteggio": 0
        }

        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(leaderboard, f, ensure_ascii=False, indent=4)


def remove_user_leaderboard(user_id):
    """
    Funzione di rimozione di un utente dal file JSON della classifica
    """
    leaderboard = load_leaderboard()

    user_id = str(user_id)
    if user_id in leaderboard:
        del leaderboard[user_id]

        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(leaderboard, f, ensure_ascii=False, indent=4)


def create_leaderboard():
    """
    Funzione di aggiornamento della classifica per ogni utente
    presente in database
    """
    for user in User.query.all():
        add_user_leaderboard(user.id)


def load_leaderboard(user_id: str = None):
    """
    Funzione di caricamento del contenuto del file JSON della classifica.
    Questa funzione è necessaria per evitare errori in caso di
    file JSON vuoto o corrotto
    """
    if not os.path.exists(LEADERBOARD_FILE):
        return {}

    try:
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            # .strip() rimuove eventuali spazi bianchi all'inizio e alla fine
            # .read() legge il contenuto del file
            content = f.read().strip()

            if not content:
                return {}  # se non c'è contenuto, ritorna dizionario vuoto

            if user_id:
                # se è specificato user_id, ritorna solo i dati di quell'utente
                # json.loads ritorna un dizionario dal contenuto del JSON
                return json.loads(content).get(user_id, {})

            # carica il contenuto trovato
            return json.loads(content)

    except json.JSONDecodeError:
        # se il file è vuoto o corrotto, ritorna comunque un dizionario vuoto
        return {}


def update_leaderboard(user_id: str, data: dict):
    """
    Funzione per aggiornare il file JSON della classifica
    con i dati passati come argomento.
    """
    leaderboard = load_leaderboard()

    if user_id in leaderboard:
        leaderboard[user_id].update(data)
    else:
        leaderboard[user_id] = data

    with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=4)
