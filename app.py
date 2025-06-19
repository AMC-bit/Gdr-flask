import os
from flask import Flask
from flask_session import Session
from gioco.routes import gioco
from battle.routes import battle
from create_character.routes import create_character
from view_characters.routes import view_characters
def create_app():
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cambia_questa_chiave_per_una_più_sicura')
    app.config['SESSION_TYPE'] = 'filesystem'

    app.register_blueprint(gioco)
    app.register_blueprint(battle)
    app.register_blueprint(create_character)
    app.register_blueprint(view_characters)
    return app

# Imposta una SECRET_KEY sicura (meglio via variabile d'ambiente)

# Inizializza il supporto alle sessioni sul filesystem


# Registra il blueprint che contiene tutte le route di gioco


if __name__ == '__main__':
    # Modalità di sviluppo con reload automatico
    app = create_app()
    app.run(debug=True)