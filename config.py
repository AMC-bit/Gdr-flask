import os

# Cartella radice del progetto (dove c’è config.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory dove tieni i JSON dei personaggi
DATA_DIR = os.path.join(BASE_DIR, 'data', 'json')
