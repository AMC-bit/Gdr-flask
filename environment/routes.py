from flask import render_template, redirect, url_for, flash, session
from . import environment_bp
from gioco.ambiente import Ambiente
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@environment_bp.route('/show-environment')
def show_environment():
    ambiente_data = session.get('ambiente')
    if not ambiente_data:
        msg = 'Nessun ambiente selezionato.'
        flash(msg, 'danger')
        logger.info(msg)
        # return redirect(url_for('environment.select_environment'))
        return redirect(url_for('mission.select_mission'))

    ambiente = Ambiente.from_dict(ambiente_data)
    msg = f"Ambiente mostrato: {ambiente.nome}"
    flash(msg, 'info')
    logger.info(msg)
    return render_template('show_environment.html', ambiente=ambiente)
