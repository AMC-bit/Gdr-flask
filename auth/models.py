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
        """Verifica se l'utente è un amministratore"""
        return self.ruolo == UserRole.ADMIN

    def is_player(self):
        """Verifica se l'utente è un giocatore"""
        return self.ruolo == UserRole.PLAYER

    def has_role(self, role):
        """Verifica se l'utente ha un ruolo specifico"""
        return self.ruolo == UserRole[role]
