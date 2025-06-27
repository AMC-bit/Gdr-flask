from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=False)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    crediti = db.Column(db.Float, nullable=False)
    personaggi = db.Column(db.String(80), nullable=False)
    character_ids = db.Column(
        JSON,               # su SQLite sarà un TEXT che SQLAlchemy serializza in JSON
        nullable=False,
        default=list        # ad ogni nuovo Utente character_ids = []
    )
