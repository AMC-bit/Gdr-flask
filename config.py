import os

# cartella root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# directory file JSON dei personaggi
DATA_DIR_PGS = os.path.join(BASE_DIR, 'data', 'json', 'personaggi')

# directory file JSON degli inventari
DATA_DIR_INV = os.path.join(BASE_DIR, 'data', 'json', 'inventari_pg')
