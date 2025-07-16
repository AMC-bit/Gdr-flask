from flask import Blueprint, render_template, request, session, redirect, url_for, Flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from auth.models import User
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user
from . import auth_bp
from app import db
from characters.routes import load_char
import re
import os
import json
import uuid

def email_check(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)


def protect_psw_hash(psw):
    return generate_password_hash(psw)


@auth_bp.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        psw = request.form['psw']
        re_psw = request.form['re_psw']
        if not name:
            raise ValueError('Name field cant be empty')
        else:
            if not email:
                raise ValueError('Email cant be empty')
            else:
                if not email_check(email):
                    raise ValueError('Email does not match an email pattern')
                else:
                    if not (psw and re_psw and psw == re_psw):
                        raise ValueError(
                            'Password and repeat Password field must match')
                    else:
                        # Registra il nuovo utente
                        hash_psw = protect_psw_hash(psw)
                        utente_exist = User.query.filter((User.email == email) and ((User.nome == name ))).first()
                        if utente_exist:
                            raise ValueError('Utente già presente')
                        else:
                            nuovo_utente = User(
                                nome=name,
                                email=email,
                                password_hash=hash_psw,
                                crediti=100,
                                character_ids=[])

                            db.session.add(nuovo_utente)
                            db.session.commit()
                        return redirect(url_for('auth.login'))
    return render_template('sign_in.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # messaggio flash se il login è errato

    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            # inserimento dato in sessione
            session['user_name'] = user.nome

            print(f"Sessione: {session}")

            return redirect(url_for('auth.personal_area'))
        else:
            flash('Email o password non corretti.', 'danger') 
            return render_template(
                'login.html')

    return render_template('login.html')


@auth_bp.route('/personal_area')
def personal_area():
    load_char()
    message = ""
    message1 = request.args.get('message', '')
    if message1:
        message = message1
    return render_template(
        "personal_area.html",
        user=current_user,
        message=message)


@auth_bp.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    user = current_user
    if user:
        if request.method == 'POST':
            # Catturo i dati inseriti nel form per la modifica dell'utente 
            # e li uso per modificare i dati dell'utente sul db,
            # infine redirige alla pagina login

            # ? Perchè non mostra il flash e perchè non prende
            # ? i value precedenti nel form ?
            new_name = request.form['new_username']
            new_email = request.form['new_email']
            new_psw = request.form['new_password']
            if user:
                id = user.id
                db_user = User.query.get_or_404(id)
                db_user.nome = new_name
                db_user.email = new_email
                if not email_check(new_email):
                    flash("Email does not match an email pattern", "error")
                else:
                    db_user.password_hash = protect_psw_hash(new_psw)
                    db.session.commit()
                    flash("Utente modificato con successo!", "success")
                    return redirect(url_for(
                        'auth.personal_area'))

    return render_template("edit_user.html", utente = user )


@auth_bp.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    utente = User.query.get(id)
    elimina_personaggi_utente(utente.character_ids)  # Elimina i personaggi dell'utente
    db.session.delete(utente)
    db.session.commit()
    return redirect(url_for('auth.sign_in'))

# Funzione per eliminare tutti i personaggi di un utente
def elimina_personaggi_utente(character_ids):
    cartella = os.path.join("data", "json", "personaggi")
    if not os.path.exists(cartella):
        return

    for filename in os.listdir(cartella):
        if filename.endswith(".json"):
            path_file = os.path.join(cartella, filename)
            try:
                with open(path_file, 'r') as f:
                    dati = json.load(f)
                # Cancella se character_ids corrisponde
                for id in character_ids:
                    if dati.get("id") == id:
                        os.remove(path_file)
                        print(f"Eliminato personaggio: {filename}")
                if dati.get("id") == current_user.character_ids:
                    os.remove(path_file)
                    print(f"Eliminato personaggio: {filename}")
            except Exception as e:
                print(f"Errore durante la verifica o cancellazione di {filename}: {e}")


@auth_bp.route('/credit_refill', methods=['GET', 'POST'])
@login_required
def credit_refill():
    message = None

    if request.method == 'POST':
        try:
            # controllo per vedere se inserimento è int
            amount = int(request.form['amount'])
        # se non è int verrà sollevata un'eccezione
        except (KeyError, ValueError):
            message = "Inserisci un numero valido."
            return redirect(url_for('auth.credit_refill', message=message))

        if amount <= 0:  # controllo numero positivo
            message = "La quantità deve essere positiva."
            return redirect(url_for('auth.credit_refill', message=message))
        else:
            current_user.crediti += amount  # aggiunta dei crediti
            db.session.commit()  # salvataggio in database
            message = (f"Ricaricati {amount} crediti. ")
            return redirect(url_for('auth.credit_refill', message=message))

    message = request.args.get('message')  # estrae il parametro message da URL
    return render_template('credit_refill.html', message=message)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logout effettuato con successo", "info")
    return render_template('menu.html')