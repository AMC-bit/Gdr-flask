## ORM SQLAlchemy, Utenti, Admin e Privilegi (Fabrice)

Questa sezione del progetto gestisce la parte **backend relativa agli utenti**, i ruoli e i privilegi, sfruttando **Flask**, **SQLAlchemy** e il modulo di autenticazione **Flask-Login**.

### Funzionalità principali

- **Gestione utenti**: registrazione, login/logout, area personale.
  - La registrazione richiede nome utente, indirizzo email, password e conferma password.
  - Login/logout per l'accesso al sistema, con funzionalità differenti in base al tipo di utente.
  - L'area personale permette di:
    - Creare personaggi (nome, classe: Mago, Ladro, Guerriero) con un oggetto a scelta come inventario iniziale.
    - Visualizzare tutti i propri personaggi e, per ognuno:
      - Visualizzare l'inventario, aggiungere o eliminare oggetti.
      - Osservare i dettagli del personaggio.
      - Modificare il nome del personaggio.
      - Eliminare il personaggio.
    - Modificare le informazioni dell'utente.
    - Caricare crediti (solo per utenti di tipo Admin).
    - Eliminare l'account utente.

- **Ruoli e privilegi**:
  - **Utente standard (Player)**: può giocare, completare missioni e interagire con NPC.
  - **Admin**: oltre ai privilegi del Player, può:
    - Caricare crediti sugli account degli utenti.
    - Modificare lo stato di un utente da Player a Admin.

- **Sicurezza**:
  - Password criptate tramite hashing (`werkzeug.security` `generate_password_hash` e `check_password_hash`).
  - Protezione delle route tramite decoratori (`@login_required`, `@admin_required`).  
    Il menu principale del gioco è protetto e accessibile solo agli utenti registrati.

- **Struttura dati**:
  - Gestione dati tramite SQLAlchemy e file JSON per salvataggi.
  - Modelli principali:
    ```python
    class UserRole(enum.Enum):
        PLAYER = "PLAYER"
        ADMIN = "ADMIN"

    class User(UserMixin, db.Model):

        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        nome = db.Column(db.String(80), nullable=False)
        email = db.Column(db.String(80), unique=True, nullable=False)
        password_hash = db.Column(db.String(128), nullable=False)
        crediti = db.Column(db.Float, nullable=False)
        ruolo = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.PLAYER)
        character_ids = db.Column(
            JSON,
            nullable=False,
            default=list
        )

        def is_admin(self):
            return self.ruolo == UserRole.ADMIN

        def is_player(self):
            return self.ruolo == UserRole.PLAYER

        def has_role(self, role: str):
            return self.ruolo == UserRole[role]
    ```

### Esempi d’uso

- **Registrazione**:
    ```bash
    Nome utente: Antonio
    Email: antonio@gamer.it
    Password: 1234
    Conferma password: 1234

    `Conferma e procedi`
    ```

- **Login**:
    ```bash
    Email: antonio@gamer.it
    Password: 1234
    ```

### Bug noti / Limiti

- Sistema di **reset password** ancora da implementare.
- Miglioramenti possibili nella sicurezza delle credenziali (lunghezza password, suggerimenti di password sicure).
- Attualmente le battaglie sono automatizzate; si potrebbe aggiungere una modalità manuale.
- Aggiungere un nuovo tipo di utente `Develop` con accesso a una sezione `Statistics` per analisi utenti e dati business.

### Update futuri

- Gestione avanzata dei privilegi per diversi tipi di Admin.
- Logging delle attività degli utenti.
- Integrazione con interfaccia web per gestione utenti da Admin.
- Possibilità di aggiungere ruoli personalizzati dinamicamente.
