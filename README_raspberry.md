# Configurazione di GDR-Flask su Raspberry

1. Alimentato il Raspberry

2. Eseguito l'accesso

3. Clonata la repository 'Gdr-flask' GitHub su Raspberry
    - `gh repo clone delectablerec/Gdr-flask`

41. Eseguito update e upgrade
    - `sudo apt update`
    - `sudo apt upgrade`

41. Installati i pacchetti necessari
    - `sudo apt install python3-venv python3-full`

42. Disattivato e rimosso il virtual environment già esistente
    - `deactivate`
    - Il comando `rm -r venv` rimuove la cartella venv, `-r` rimuove anche le sottocartelle

4. Creato e attivato il virtual environment
    - `python -m venv venv`
    - `source venv/bin/activate`

5. Installate le librerie necessarie grazie al file 'requirements.txt'
    - `pip install -r requirements.txt`

6. Run dell'applicazione
    - `python app.py`