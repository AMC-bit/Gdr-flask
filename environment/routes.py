from flask import request, render_template, redirect, url_for, flash, session
from . import environment_bp
from gioco.ambiente import AmbienteFactory, Ambiente


@environment_bp.route('/select-environment', methods=['GET', 'POST'])
def select_environment():
    if request.method == 'POST':
        ambiente_id = request.form.get('ambiente_id')
        ambiente = AmbienteFactory.seleziona_da_id(ambiente_id)
        session['ambiente'] = ambiente.to_dict()  # Salva l'ambiente in sessione
        flash(f'Ambiente selezionato: {ambiente.nome}', 'success')
        return redirect(url_for('environment_bp.show_environment'))

    ambienti = AmbienteFactory.get_opzioni()
    return render_template('select_environment.html', ambienti=ambienti)


@environment_bp.route('/show-environment')
def show_environment():
    ambiente_data = session.get('ambiente')
    if not ambiente_data:
        flash('Nessun ambiente selezionato.', 'warning')
        return redirect(url_for('environment_bp.select_environment'))

    ambiente = Ambiente.from_dict(ambiente_data)
    return render_template('show_environment.html', ambiente=ambiente)