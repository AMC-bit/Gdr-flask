from . import auth_bp
from flask import render_template, request, redirect, url_for, session, abort
from gioco.personaggio import Personaggio
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return render_template("logout.html")


@auth_bp.route('/area_riservata', methods=['GET', 'POST'])
@login_required
def area_personale():
    return render_template('area_riservata.html')


@auth_bp.route('/credit_refill', methods=['GET', 'POST'])
@login_required
def credit_refill():
    message = None

    if request.method == 'POST':
        try:
            amount = int(request.form['amount'])  # controllo per vedere se inserimento è int
        except (KeyError, ValueError):  # se non è int verrà sollevata un'eccezione
            message = "Inserisci un numero valido."
            return render_template('credit_refill.html', message=message)

        if amount <= 0:  # controllo numero positivo
            message = "La quantità deve essere positiva."
        else:
            current_user.crediti += amount  # aggiunta dei crediti
            db.session.commit()  # salvataggio in database
            message = f"Ricaricati {amount} crediti. Totale attuale: {current_user.crediti}."

    return render_template('credit_refill.html', message=message)