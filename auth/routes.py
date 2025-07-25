from flask import render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from auth.models import User, UserRole, db
from . import auth_bp
from characters.routes import load_char
import re
import os
import json


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
        ruolo_sel = request.form['ruolo'] if 'ruolo' in request.form else 'PLAYER'

        if not name:
            flash("Il nome è necessario", 'danger')
            return render_template('sign_in.html', email=email)
        if not email:
            flash("La email è necessaria", 'danger')
            return render_template('sign_in.html', name=name)
        if not email_check(email):
            flash('Inserisci una mail corretta', 'danger')
            return render_template('sign_in.html', name=name)
        if not (psw and re_psw and psw == re_psw):
            flash('Password e conferma password non combaciano', 'danger')
            return render_template('sign_in.html', name=name, email=email)

        hash_psw = protect_psw_hash(psw)

        utente_exist = (
            User.query
            .filter(User.email == email)
            .first()
        )
        if utente_exist:
            flash('Email già registrata', 'danger')
            return render_template('sign_in.html', name=name, email=email)

        nuovo_utente = User(
            nome=name,
            email=email,
            password_hash=hash_psw,
            crediti=100,
            character_ids=[],
            ruolo=UserRole[ruolo_sel] if ruolo_sel in UserRole.__members__ else UserRole.PLAYER
        )
        db.session.add(nuovo_utente)
        db.session.commit()

        flash("Sei registrato. Ora effettua il login", "success")
        return redirect(url_for('auth.login'))

    return render_template('sign_in.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        # login non riuscito
        if not user or not check_password_hash(user.password_hash, password):
            flash('Email o password non corretti', 'danger')
            return render_template('login.html', email=email)

        # login riuscito
        login_user(user)
        session['user_name'] = user.nome

        return redirect(url_for('auth.personal_area'))

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

    if request.method == 'POST':
        # catturo i dati inseriti nel form per la modifica dell'utente
        new_name = request.form['new_username']
        new_email = request.form['new_email']
        new_psw = request.form['new_password']

        if not email_check(new_email):
            flash("Email does not match an email pattern", "danger")
            return render_template(
                'edit_user.html',
                utente=user,
                new_name=new_name,
                new_email=new_email
            )

        # modifico i dati dell'utente
        user.nome = new_name
        user.email = new_email
        user.password_hash = protect_psw_hash(new_psw)
        db.session.commit()  # salvataggio su db

        flash("Utente modificato con successo!", "success")
        # ritorno all'area personale
        return redirect(url_for('auth.personal_area'))

    return render_template("edit_user.html", utente=user)


@auth_bp.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    utente = User.query.get(id)

    # elimina i personaggi dell'utente
    elimina_personaggi_utente(utente.character_ids)
    # elimina gli inventari dell'utente
    elimina_inventari_utente(utente.character_ids)

    db.session.delete(utente)
    db.session.commit()
    return redirect(url_for('auth.sign_in'))


# funzione per eliminare tutti i personaggi di un utente
def elimina_personaggi_utente(character_ids):
    cartella_personaggi = os.path.join("data", "json", "personaggi")
    if not os.path.exists(cartella_personaggi):
        return

    for filename in os.listdir(cartella_personaggi):
        if filename.endswith(".json"):
            path_file = os.path.join(cartella_personaggi, filename)
            try:
                with open(path_file, 'r', encoding="utf-8") as f:
                    dati = json.load(f)

                # Cancella se character_ids corrisponde
                for char_id in character_ids:
                    if dati.get("id") == char_id:
                        os.remove(path_file)
                        print(f"Eliminato personaggio: {filename}")
                if dati.get("id") == current_user.character_ids:
                    os.remove(path_file)
                    print(f"Eliminato personaggio: {filename}")
            except Exception as e:
                print(f"Errore durante la verifica o cancellazione di {filename}: {e}")

# funzione per eliminare gli inventari di un utente
def elimina_inventari_utente(character_ids):
    cartella_inventari = os.path.join("data", "json", "inventari")
    if not os.path.exists(cartella_inventari):
        return

    for filename in os.listdir(cartella_inventari):
        if filename.endswith(".json"):
            path_file = os.path.join(cartella_inventari, filename)
            try:
                with open(path_file, 'r', encoding="utf-8") as f:
                    dati = json.load(f)

                # Cancella se id_proprietario corrisponde
                if dati.get("id_proprietario") in character_ids:
                    os.remove(path_file)
                    print(f"Eliminato inventario: {filename}")
            except Exception as e:
                print(f"Errore durante la cancellazione dell'inventario {filename}: {e}")


@auth_bp.route('/credit_refill', methods=['GET', 'POST'])
@auth_bp.route('/credit_refill/<int:user_id>', methods=['GET', 'POST'])
@login_required
def credit_refill(user_id=None):
    # Controllo se l'utente è un amministratore
    # altrimenti si viene ridiretti all'area personale
    # Solo gli amministratori possono ricaricare i crediti
    if not current_user.is_admin():
        flash("Accesso negato", "danger")
        return redirect(url_for('auth.personal_area'))

    if user_id:
        target_user = User.query.get_or_404(user_id)
    else:
        target_user = current_user
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
            target_user.crediti += amount  # aggiunta dei crediti
            db.session.commit()  # salvataggio in database

            if target_user.id != current_user.id:
                message = f"Ricaricati {amount} crediti per {target_user.nome}."
                return redirect(url_for('auth.admin_manager', message=message))
            else:
                message = f"Ricaricati {amount} crediti."
                return redirect(url_for('auth.credit_refill', message=message))

    message = request.args.get('message')  # estrae il parametro message da URL
    return render_template('credit_refill.html', message=message)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logout effettuato con successo", "success")
    return render_template('menu.html')