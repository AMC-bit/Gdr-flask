from flask import Blueprint, render_template, request, session, redirect, url_for, Flask

# Istanze di test
from gioco.personaggio import Personaggio
from gioco.classi import Mago, Guerriero, Ladro
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
gioco = Blueprint('gioco', __name__, template_folder=template_dir)


@gioco.route('/sign_in')
def sign_in():
    if request.method == 'POST':
        email = request.form['email'].strip()
        psw = request.form['psw']
        re_psw = request.form['re_psw']
        
    return render_template('sign_in.html')