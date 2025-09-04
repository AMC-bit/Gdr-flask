## ORM SQLAlchemy, Utenti, Admin e Privilegi (Fabrice)

Questa sezione del progetto gestisce la parte **backend relativa agli utenti**, i ruoli e i privilegi, sfruttando **Flask**, **SQLAlchemy** e il modulo di autenticazione **Flask-Login**.

### Funzionalità principali

- **Gestione utenti**: registrazione, login/logout, area personale.
    La registrazione viene gestita con l'inserimento nome utente, indirizzo mail, password e conferma passworrd.
    Login logout per l'accesso del singolo utente che da accesso a delle funzionalità a secondo della tipologia dell'utente
    L'area personale permette di gestire la creazione(eliminazione) dei personaggi, modifica dei parametri utente(cancellazione account,
    modificare nome utente, oppure mail, )
- **Ruoli e privilegi**:
  - Utente standard: può giocare, completare missioni e interagire con NPC.
  - Admin: può gestire contenuti del gioco, missioni e utenti.
- **Sicurezza**:
  - Password criptate tramite hashing (werkzeug.security `generate_password_hash` e `check_password_hash`).
  - Protezione delle route tramite decoratori (`@login_required`, `@admin_required`).
- **Struttura dati**:
  - Modelli SQLAlchemy principali:
    ```python

    ```
  - Relazioni future con altri modelli (Missioni, Oggetti, Personaggi) tramite chiavi esterne.

### Esempi d’uso

- **Registrazione**:
    ```python

    ```
- **Login**:
    ```python

    ```
- **Protezione route admin**:
    ```python

    ```

### Bug noti / Limiti
- Ancora da implementare un sistema di **reset password**. Dare la possibilità all'utente di recuperare la password.
- Aumento della sicurezza delle credenziali(nome utente, lunghezza password, proposta automatica della password)
- Abbiamo implementato una versione automatizzata progetto. Si potrebbe migliorare con una versione della bataglia non 
  automatizzata.
- Aggiunta di una nuova tipologia di utente `Develop` che avrebbe accesso a una nuova sezione `statistics` che permetterebbe di aver un feedback per la geszione
  della parte data analist e data science del progetto. In modo a capire il profilo degli utenti, le loro proposte, e la parte buisness del progetto
- 

### Update futuri
- Gestione avanzata dei privilegi per diversi tipi di admin.
- Log attività utente.
- Integrazione con interfaccia web per gestione utenti da admin.
- Possibilità di aggiungere ruoli personalizzati dinamicamente.

