# Configurazione di GDR-Flask su Raspberry

1. Alimentato il Raspberry

2. Eseguito l'accesso

3. Clonata la repository 'Gdr-flask' GitHub su Raspberry
    - `gh repo clone delectablerec/Gdr-flask`

4. Eseguito update e upgrade
    - `sudo apt update`
    - `sudo apt upgrade`

5. Installati i pacchetti necessari
    - `sudo apt install python3-venv python3-full`

6. Disattivato e rimosso il virtual environment già esistente
    - `deactivate`
    - Il comando `rm -r venv` rimuove la cartella venv, `-r` rimuove anche le sottocartelle

7. Creato e attivato il virtual environment
    - `python -m venv venv`
    - `source venv/bin/activate`

8. Installate le librerie necessarie grazie al file 'requirements.txt'
    - `pip install -r requirements.txt`

9. Run dell'applicazione
    - `python app.py`