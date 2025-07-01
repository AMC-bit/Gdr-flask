from flask import Blueprint, render_template, request, session, redirect, url_for, Flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from auth.models import User
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user
from . import auth_bp
from app import db
import os
import re


def controllo_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)


def psw_proteggi_hash(psw):
    return generate_password_hash(psw)


@auth_bp.route('/sign_in', methods=['GET', 'POST'])
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
                        utente_exist = User.query.filter((User.email == email)and((User.nome == name ))).first()
                        if utente_exist:
                            raise ValueError('Utente già presente')
                        else:
                                nuovo_utente = User(nome= name, email= email, password_hash= hash_psw, crediti= 100, character_ids=[])
                                db.session.add(nuovo_utente)
                                db.session.commit()
                        return redirect(url_for('auth.login'))
    return render_template('sign_in.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('auth.area_personale'))
        else:
            return render_template('login.html', error='Credenziali non valide.')

    return render_template('login.html')


@auth_bp.route('/area_personale')
def area_personale():
    message = ""
    message1 = request.args.get('message', '')
    if message1:
        message = message1
    return render_template("area_personale.html", user=current_user, message=message)


@auth_bp.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    enable_edit_user= False
    user = None
    psw = ""
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        # Questa parte fa il controllo della  psw iniziale e fa spawnare il form
        # per la modifica dei dati dell'utente
        if form_type=='check_form':
            psw = request.form['password']
            user = current_user
            if user and check_password_hash(user.password_hash, psw):
                enable_edit_user= True
   
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        #Catturo i dati inseriti nel form per la modifica dell'utente e li uso per 
        #modificare i dati dell'utente sul db, invine redirige alla pagina login
        if form_type=='edit_form':
            new_name = request.form['new_username']
            new_email = request.form['new_email']
            new_psw = request.form['new_password']
            user = current_user
            if user:
                id = user.id
                db_user = User.query.get_or_404(id)
                db_user.nome = new_name
                db_user.email = new_email
                db_user.password_hash = psw_proteggi_hash(new_psw)
                db.session.commit()
                message = "Utente modificato con successo!"
                return redirect(url_for('auth.area_personale', message=message))
            
    return render_template("edit_user.html", enable_edit_user = enable_edit_user, utente = user, password = psw  )



@auth_bp.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    utente = User.query.get(id)
    db.session.delete(utente)
    db.session.commit()
    return redirect(url_for('auth.sign_in'))

@auth_bp.route('/credit_refill', methods=['GET', 'POST'])
@login_required
def credit_refill():
    message = None

    if request.method == 'POST':
        try:
            amount = int(request.form['amount'])  # controllo per vedere se inserimento è int
        except (KeyError, ValueError):  # se non è int verrà sollevata un'eccezione
            message = "Inserisci un numero valido."
            return redirect(url_for('auth.credit_refill', message=message))

        if amount <= 0:  # controllo numero positivo
            message = "La quantità deve essere positiva."
            return redirect(url_for('auth.credit_refill', message=message))
        else:
            current_user.crediti += amount  # aggiunta dei crediti
            db.session.commit()  # salvataggio in database
            message = f"Ricaricati {amount} crediti. Totale attuale: {int(current_user.crediti)}."
            return redirect(url_for('auth.credit_refill', message=message))

    message = request.args.get('message')  # estrae il parametro message dall'URL
    return render_template('credit_refill.html', message=message)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout effettuato con successo", "info")
    return render_template('menu.html')