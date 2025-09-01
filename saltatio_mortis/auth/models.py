from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.dialects.sqlite import JSON
import enum


db = SQLAlchemy()

class UserRole(enum.Enum):
    PLAYER = "PLAYER"
    ADMIN = "ADMIN"
    TESTER = "TESTER"  # Ruolo esempio per il futuro

class User(UserMixin, db.Model):
    """
    Rappresenta un utente nel sistema.
    Attributes:
        id (int): Identificatore univoco dell'utente.
        nome (str): Nome dell'utente.
        email (str): Email dell'utente, deve essere unica.
        password_hash (str): Hash della password dell'utente.
        crediti (float): Crediti disponibili per l'utente.
        ruolo (UserRole): Ruolo dell'utente nel sistema
            (PLAYER, ADMIN, TESTER).
        character_ids (list): Lista degli ID dei personaggi associati
            all'utente.

    Methods:
        is_admin: Verifica se l'utente è un amministratore.
        is_player: Verifica se l'utente è un giocatore.
        has_role: Verifica se l'utente ha un ruolo specifico.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    crediti = db.Column(db.Float, nullable=False)
    ruolo = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.PLAYER)
    character_ids = db.Column(
        JSON,               # su SQLite sarà un TEXT che SQLAlchemy serializza in JSON
        nullable=False,
        default=list        # ad ogni nuovo Utente character_ids = []
    )

    def is_admin(self):
        """
        Verifica se l'utente è un amministratore.
        Returns:
            bool: True se l'utente è un amministratore, False altrimenti.
        """
        return self.ruolo == UserRole.ADMIN

    def is_player(self):
        """
        Verifica se l'utente è un giocatore.
        Returns:
            bool: True se l'utente è un giocatore, False altrimenti.
        """
        return self.ruolo == UserRole.PLAYER

    def has_role(self, role: str):
        """
        Verifica se l'utente ha un ruolo specifico.
        Args:
            role (str): Il nome del ruolo da verificare.

        Returns:
            bool: True se l'utente ha il ruolo specificato, False altrimenti.
        """
        return self.ruolo == UserRole[role]
