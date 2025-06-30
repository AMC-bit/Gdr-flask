from flask import Blueprint, render_template, request, session, redirect, url_for, Flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from auth.models import User, db
import os
import re
from . import auth_bp


def controllo_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def psw_proteggi_hash(psw):
    return generate_password_hash(psw)

@auth_bp .route('/sign_in')
def sign_in():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        psw = request.form['psw']
        re_psw = request.form['re_psw']
        if not  name :
            raise ValueError('Name field cant be empty')
        else:
            if not email:
                raise ValueError('Email cant be empty')
            else:
                if not controllo_email(email):
                    raise ValueError('Email does not match an email pattern')
                else:
                    if not ( psw and re_psw and psw == re_psw) :
                        raise ValueError('Password and repeat Password field must match')
                    else:
                        #Registra il nuovo utente
                        hash_psw = psw_proteggi_hash(psw)
                        #TODO qua  hash_psw e email vanno inseriti all'interno del db
                        #Controllo che nel db non ci sia già un utente con quel nome e psw
                        utente_exist = User.query.filter((User.email == email)|((User.nome == name ))).first()
                        if utente_exist:
                            raise ValueError('Utente già presente')
                        else:
                            #Creo un istanza di user e la metto nel db
                                nuovo_utente = User(nome= name, email= email, password_hash= hash_psw, crediti= 100, personaggi=[])
                                db.session.add(nuovo_utente)
                                db.session.commit()
                        return redirect(url_for('login'))
    return render_template('sign_in.html')