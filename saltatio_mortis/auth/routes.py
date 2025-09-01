from flask import render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from auth.models import User, UserRole, db
from . import auth_bp
from characters.routes import load_char
from config import add_user_leaderboard, remove_user_leaderboard
import re
import os
import json


def email_check(email: str) -> bool:
    """
    Controlla che l'email inserita sia corretta

    Args:
        email (str): email

    Returns:
        bool: True se corrisponde al pattern
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)


def protect_psw_hash(psw: str) -> str:
    """
    Funzione di protezione della password

    Args:
        psw (str): password

    Returns:
        str: password hash
    """
    return generate_password_hash(psw)


@auth_bp.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    """
    Registrazione nuovo utente.
    Metodo GET: ritorna il template alla pagina di registrazione
    Metodo POST: esegue i vari controlli e registra l'utente in database
    mostrando un messaggio di successo e reindirizzando alla pagina di login

    Returns:
        flask.Response: template HTML di registrazione oppure login
    """
    if request.method == 'POST':
        name = request.form['name'].strip().capitalize()
        email = request.form['email'].strip()
        psw = request.form['psw']
        re_psw = request.form['re_psw']

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
            ruolo=UserRole.PLAYER
        )
        db.session.add(nuovo_utente)
        db.session.commit()

        add_user_leaderboard(nuovo_utente.id) # aggiunge utente a classifica

        flash("Sei registrato. Ora effettua il login", "success")
        return redirect(url_for('auth.login'))

    return render_template('sign_in.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login utente.
    Metodo GET: ritorna il template alla pagina di login
    Metodo POST: esegue il login dell'utente, mostrando un messaggio di
        errore se non riesce

    Returns:
        flask.Response: template HTML di login
            oppure reindirizza all'area personale dell'utente
    """
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
    """
    Area personale dell'utente.
    Mostra i dati dell'utente e un messaggio se presente.
    Metodo GET: ritorna il template dell'area personale

    Returns:
        flask.Response: template HTML dell'area personale
    """
    load_char()
    message = ""
    message1 = request.args.get('message', '')
    if message1:
        message = message1
    return render_template(
        "personal_area.html",
        user=current_user,
        is_admin=current_user.is_admin(),
        message=message)


@auth_bp.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    """
    Modifica i dati dell'utente.
    Metodo GET: ritorna il template per la modifica dell'utente
    Metodo POST: esegue i vari controlli e modifica i dati dell'utente
        mostrando un messaggio di successo e reindirizzando all'area personale

    Returns:
        flask.Response: template HTML per la modifica dell'utente
    """
    user = current_user

    if request.method == 'POST':
        # catturo i dati inseriti nel form per la modifica dell'utente
        new_name = request.form['new_username'].strip().capitalize()
        new_email = request.form['new_email'].strip()
        new_psw = request.form['new_password'].strip()

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
    """
    Elimina un utente.
    Metodo GET: elimina l'utente con l'id specificato, rimuovendo i suoi
    personaggi e inventari associati, e reindirizza alla pagina di login

    Args:
        id (int): ID dell'utente da eliminare

    Returns:
        flask.Response: reindirizza alla pagina di login
    """
    utente = User.query.get(id)

    # elimina i personaggi dell'utente
    elimina_personaggi_utente(utente.character_ids)
    # elimina gli inventari dell'utente
    elimina_inventari_utente(utente.character_ids)

    db.session.delete(utente)
    db.session.commit()

    remove_user_leaderboard(utente.id)

    return redirect(url_for('auth.sign_in'))


# funzione per eliminare tutti i personaggi di un utente
def elimina_personaggi_utente(character_ids: list):
    """
    Elimina tutti i personaggi di un utente.
    Controlla se esistono file JSON dei personaggi e li elimina
    se gli ID corrispondono a quelli della lista dell'utente che si vuole
    rimuovere.

    Args:
        character_ids (list): Lista degli ID dei personaggi da eliminare.
    Returns:
        None: Non ritorna nulla, ma elimina i file JSON dei personaggi
    Raises:
        Exception: Se si verifica un errore durante la lettura o
            la cancellazione dei file
    """
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
def elimina_inventari_utente(character_ids: list):
    """
    Elimina gli inventari dei personaggi di un utente.
    Controlla se esistono file JSON degli inventari e li elimina
    se gli ID corrispondono a quelli della lista dell'utente che si vuole
    rimuovere.

    Args:
        character_ids (list): Lista degli ID dei personaggi di cui
            eliminare gli inventari.

    Returns:
        None: Non ritorna nulla, ma elimina i file JSON degli inventari

    Raises:
        Exception: Se si verifica un errore durante la lettura o
            la cancellazione dei file
    """
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


# Admin manager
@auth_bp.route('/manage_users')
@login_required
def admin_manager():
    """
    Gestisce gli utenti del sistema.
    Se l'utente è un amministratore, mostra la lista degli utenti
    e permette di modificare i loro ruoli e ricaricare i loro crediti.
    Altrimenti, reindirizza all'area personale dell'utente.
    Metodo GET: mostra la lista degli utenti e permette di modificare i loro
    ruoli e ricaricare i loro crediti.

    Returns:
        flask.Response: template HTML per la gestione degli utenti o se non
        si è amministratori, reindirizza all'area personale dell'utente.
    """
    # Controllo: solo admin può accedere
    if not current_user.is_admin():
        flash(
            "Accesso negato. "
            "Solo gli amministratori possono gestire gli utenti.",
            "danger"
        )
        return redirect(url_for('auth.personal_area'))

    # Recupera tutti gli utenti dal database
    users = User.query.all()
    message = request.args.get('message')

    return render_template('admin_manager.html', users=users, message=message)

@auth_bp.route('/update_user_role', methods=['POST'])
@login_required
def update_user_role():
    """
    Aggiorna il ruolo di un utente.
    Metodo POST: aggiorna il ruolo dell'utente selezionato
    e reindirizza alla pagina di gestione degli utenti.
    Se l'utente non è un amministratore,
    mostra un messaggio di accesso negato ed è reindirizzato
    all'area personale.
    C'è un controllo per impedire a un amministratore
    di modificare il proprio ruolo.

    Raises:
        KeyError: Se i dati del form non sono validi.
    Returns:
        flask.Response: reindirizza alla pagina di gestione degli utenti se
            l'utente è un amministratore, altrimenti reindirizza all'area 
            personale.
    """
    # Controllo: solo admin può accedere
    if not current_user.is_admin():
        flash(
            "Accesso negato. Solo gli amministratori possono "
            "modificare i ruoli.",
            "danger"
            )
        return redirect(url_for('auth.personal_area'))

    try:
        # Estrazione dati dal form
        user_id = int(request.form['user_id'])
        new_role = request.form['ruolo']
    except (KeyError, ValueError):
        flash("Dati del form non validi.", "danger")
        return redirect(url_for('auth.admin_manager'))

    # Blocco: impedisce a un admin di modificare il proprio ruolo
    if user_id == current_user.id:
        flash("Non puoi modificare il tuo stesso ruolo.", "warning")
        return redirect(url_for('auth.admin_manager'))

    # Recupero utente dal DB
    user = User.query.get_or_404(user_id)

    try:
        user.ruolo = UserRole[new_role]
    except KeyError:
        flash("Ruolo selezionato non valido.", "danger")
        return redirect(url_for('auth.admin_manager'))

    # Salvataggio nel DB
    db.session.commit()
    flash(f"Ruolo aggiornato a {new_role} per {user.nome}.", "success")
    return redirect(url_for('auth.admin_manager'))


@auth_bp.route('/credit_refill', methods=['GET', 'POST'])
@auth_bp.route('/credit_refill/<int:user_id>', methods=['GET', 'POST'])
@login_required
def credit_refill(user_id=None):
    """
    Ricarica i crediti di un utente.
    Metodo GET: mostra il form per la ricarica dei crediti
    Metodo POST: esegue la ricarica dei crediti per l'utente specificato
        o per l'utente corrente se non viene specificato un user_id.
    Se l'utente non è un amministratore, mostra un messaggio di accesso
    negato e reindirizza all'area personale dell'utente.

    Args:
        user_id (int, optional): ID dell'utente per cui ricaricare i crediti.
            Se non specificato, ricarica i crediti dell'utente corrente.

    Raises:
        KeyError: Se i dati del form non sono validi.
        ValueError: Se l'importo inserito non è un numero valido.

    Returns:
        flask.Response: template HTML per la ricarica dei crediti o se
        non si è amministratori, reindirizza all'area personale dell'utente.
    """
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
            # Controlla se c'è un user_id nascosto nel form (per la gestione di altri utenti)
            form_user_id = request.form.get('user_id')
            if form_user_id:
                target_user = User.query.get_or_404(form_user_id)

            # controllo per vedere se inserimento è int
            amount = int(request.form['amount'])
        # se non è int verrà sollevata un'eccezione
        except (KeyError, ValueError):
            message = "Inserisci un numero valido."
            if target_user.id != current_user.id:
                return redirect(
                    url_for(
                        'auth.credit_refill',
                        user_id=target_user.id,
                        message=message
                    )
                )
        else:
            return redirect(url_for('auth.credit_refill', message=message))

        if amount <= 0:  # controllo numero positivo
            message = "La quantità deve essere positiva."
            if target_user.id != current_user.id:
                return redirect(
                    url_for(
                        'auth.credit_refill',
                        user_id=target_user.id,
                        message=message
                    )
                )
            else:
                return redirect(url_for('auth.credit_refill', message=message))
        else:
            target_user.crediti += amount  # aggiunta dei crediti
            db.session.commit()  # salvataggio in database

            if target_user.id != current_user.id:
                message = (
                    f"Ricaricati {amount} crediti per {target_user.nome}."
                )
                return redirect(url_for('auth.admin_manager', message=message))
            else:
                message = f"Ricaricati {amount} crediti."
                return redirect(
                    url_for(
                        'auth.credit_refill',
                        message=message,
                        modified=True
                    )
                )
    # estrae il parametro message da URL
    message = request.args.get('message')
    # controlla se è stata fatta una modifica
    modified = request.args.get('modified', False)
    return render_template(
        'credit_refill.html',
        message=message,
        target_user=target_user,
        modified=modified
    )


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Effettua il logout dell'utente.
    Metodo GET: effettua il logout dell'utente, rimuovendo i dati di sessione.
    Mostra un messaggio di successo e reindirizza alla pagina di login.
    Returns:
        flask.Response: reindirizza alla pagina di login con un messaggio di
            successo.
    """
    logout_user()
    session.clear()
    flash("Logout effettuato con successo", "success")
    # Invece di render_template('menu.html'))
    return redirect(url_for('home.index'))
