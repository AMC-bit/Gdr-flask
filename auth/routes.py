from flask import Blueprint, render_template, request, session, redirect, url_for, Flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import os
import re


def controllo_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def psw_proteggi_hash(psw):
    return generate_password_hash(psw)

@auth_bp .route('/sign_in')
def sign_in():
    if request.method == 'POST':
        email = request.form['email'].strip()
        psw = request.form['psw']
        re_psw = request.form['re_psw']

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
                    """
                    utente_exist = Utente.query.filter((Utente.email == email)|((Utente.nome == nome )& (Utente.cognome == cognome))).first()
                    if utente_exist:
                        messaggio="utente già presente nel db"
                    else:
                        if nome:
                            nuovo_utente = Utente(nome= nome, cognome = cognome, email= email, password_hash=generate_password_hash(password))
                            db.session.add(nuovo_utente)
                            db.session.commit()
                    """
                    return redirect(url_for('login'))
    return render_template('sign_in.html')