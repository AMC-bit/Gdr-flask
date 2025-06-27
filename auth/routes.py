from . import auth_bp
from flask import render_template, request, redirect, url_for
from flask_login import login_user
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    messaggio = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        utente = Utente.query.filter_by(username=username).first()
        if utente and utente.check_password(password):
            login_user(utente)
            return render_template("area_personale.html")
        else:
            messaggio = "username o password errati!"
    return render_template("login.html", messaggio=messaggio)


@auth_bp.route('/area_personale')
def area_personale():
    return render_template("area_personale.html")

@auth_bp.route('/edit_user')
def edit_user():
    # Logica per modificare le informazioni dell'utente
    # L'utente inserirà la password attuale per verificare la persona
    # L'utente potrà inserire le nuove informazioni sia per nome utente che per la password
    return render_template("edit_user.html")

@auth_bp.route('/delete_user')
def delete_user():
    # Logica per eliminare l'utente
    # Un messaggio di avviso apparirà per confermare l'eliminazione
    return render_template("area_personale.html")
