from flask import request, render_template, redirect, url_for, flash, session
from . import environment_bp
from gioco.ambiente import AmbienteFactory, Ambiente
from utils.log import Log


@environment_bp.route('/select-environment', methods=['GET', 'POST'])
def select_environment():
    if request.method == 'POST':
        ambiente_id = request.form.get('ambiente_id')
        ambiente = AmbienteFactory.seleziona_da_id(ambiente_id)
        session['ambiente'] = ambiente.to_dict()
        # Salva l'ambiente in sessione
        msg = f"Ambiente selezionato: {ambiente.nome} (id: {ambiente_id})"
        flash(msg, 'success')
        Log.scrivi_log(msg)
        return redirect(url_for('environment.show_environment'))

    ambienti = AmbienteFactory.get_opzioni()
    return render_template('select_environment.html', ambienti=ambienti)


@environment_bp.route('/show-environment')
def show_environment():
    ambiente_data = session.get('ambiente')
    if not ambiente_data:
        msg = 'Nessun ambiente selezionato.'
        flash(msg, 'error')
        Log.scrivi_log(msg)
        # return redirect(url_for('environment.select_environment'))
        return redirect(url_for('mission.select_mission'))

    ambiente = Ambiente.from_dict(ambiente_data)
    msg = f"Ambiente mostrato: {ambiente.nome}"
    flash(msg, 'info')
    Log.scrivi_log(msg)
    return render_template('show_environment.html', ambiente=ambiente)


@staticmethod
def descrizione():
    from gioco.classi import Mago, Ladro, Guerriero

    from gioco.oggetto import Oggetto, PozioneCura, Medaglione, BombaAcida
    from copy import deepcopy

    ambiente = session.get('ambiente')
    if isinstance(ambiente, dict):
        ambiente = Ambiente.from_dict(ambiente)

    oggetti = [PozioneCura(), Medaglione(), BombaAcida()]
    classi = {
        'Mago': Mago("x"), 'Ladro': Ladro("y"), 'Guerriero': Guerriero("z")
    }

    classe = classi['Guerriero']
    val_standard_guerriero = {
        'attacco': {
            'da': classe.attacco_min + 15,
            'a': classe.attacco_max + 20
        },
        'cura': {'recupero salute': f"{30}"}
    }

    classe = classi['Ladro']
    val_standard_ladro = {
        'attacco': {
            'da': classe.attacco_min + 5,
            'a': classe.attacco_max + 5
        },
        'cura': {'recupero salute': f"da {10} a {40}"}
    }

    classe = classi['Mago']
    val_standard_mago = {
        'attacco': {
            'da': classe.attacco_min - 5,
            'a': classe.attacco_max + 10
        },
        'cura': {'recupero salute':  f"{20}% salute rimanente"}
    }

    val_standard_oggetti = {}
    for oggetto in oggetti:
        if isinstance(oggetto, Oggetto):
            class_name = oggetto.__class__.__name__
            val_standard_oggetti[class_name] = {
                'valore': oggetto.valore,
                'tipo_oggetto': oggetto.tipo_oggetto,
            }

    val_standard = {
        'Guerriero': val_standard_guerriero,
        'Ladro': val_standard_ladro,
        'Mago': val_standard_mago,
        'Oggetto': val_standard_oggetti
    }

    var_attacco_amb = {}
    var_cura_amb = {}
    var_amb = deepcopy(val_standard)

    for chiave in classi:
        classe = classi[chiave]
        istanza = chiave
        var_attacco_amb[istanza] = int(ambiente.modifica_attacco(classe))
        var_cura_amb[istanza] = int(ambiente.modifica_cura(classe))

        print(
            f"DEBUG - {chiave}: attacco={var_attacco_amb[istanza]}, "
            f"cura={var_cura_amb[istanza]}"
        )

    for chiave in var_amb:
        valore = var_amb[chiave]
        if chiave in var_attacco_amb and 'attacco' in valore:
            n_att = var_attacco_amb[chiave]
            if n_att != 0:
                if not chiave == 'Guerriero':
                    valore['attacco']['da'] = (
                        int(valore['attacco']['da']) + int(n_att)
                    )
                valore['attacco']['a'] += n_att

        if chiave in var_cura_amb and 'cura' in valore:
            n_cura = var_cura_amb[chiave]
            if n_cura != 0:
                if chiave == 'Mago':
                    if n_cura > 0:
                        x = f"+ {n_cura}"
                    else:
                        x = f"- {abs(n_cura)}"
                    valore['cura']['recupero salute'] = (
                        f"20% (salute rimanente {x})"
                    )
                if chiave == 'Ladro':
                    valore['cura']['recupero salute'] = (
                        f"da {10 + n_cura} a {40 + n_cura}"
                    )
                if chiave == 'Guerriero':
                    valore['cura']['recupero salute'] = f"{30 + n_cura}"

        elif chiave == 'Oggetto':
            for obj in oggetti:
                n_obj = ambiente.modifica_effetto_oggetto(obj)
                obj_name = obj.__class__.__name__
                if obj_name in valore and n_obj != 0:
                    valore[obj_name]['valore'] += n_obj

    print(f"val_standard: {val_standard}")
    print(f"var_amb: {var_amb}")

    return {'val_standard': val_standard, 'var_amb': var_amb}
