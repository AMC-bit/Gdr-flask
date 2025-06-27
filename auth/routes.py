from . import auth_bp
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# configurazione dell'app Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///utenti.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.secret_key = 'chiave'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
class Utente(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
@login_manager.user_loader
def load_user(user_id):
    return Utente.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    messaggio = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        utente = Utente.query.filter_by(username=username).first()
        if utente and utente.check_password(password):
            login_user(utente)
            return redirect(url_for('utenti'))
        else:
            messaggio = "username o password errati!"
    return render_template("login.html", messaggio=messaggio)