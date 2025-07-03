import os

# Cartella radice del progetto (dove c’è config.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory dove tieni i JSON
DATA_DIR = os.path.join(BASE_DIR, 'data', 'json')

# Percorso completo a characters.json
CHAR_FILE = os.path.join(DATA_DIR, 'characters.json')