import os
from flask import Flask
from flask_session import Session
from gioco.routes import gioco
from battle.routes import battle_bp
from create_character.routes import create_character_bp
from view_characters.routes import view_characters_bp
from select_environment.routes import select_environment_bp
from inventory.routes import inventory_bp
from select_mission.routes import select_mission_bp
def create_app():
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cambia_questa_chiave_per_una_più_sicura')
    app.config['SESSION_TYPE'] = 'filesystem'

    #app.register_blueprint(gioco)
    app.register_blueprint(battle_bp)
    app.register_blueprint(create_character_bp)
    app.register_blueprint(view_characters_bp)
    app.register_blueprint(select_environment_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(select_mission_bp)

    return app

# Imposta una SECRET_KEY sicura (meglio via variabile d'ambiente)

# Inizializza il supporto alle sessioni sul filesystem


# Registra il blueprint che contiene tutte le route di gioco


if __name__ == '__main__':
    # Modalità di sviluppo con reload automatico
    app = create_app()
    app.run(debug=True)