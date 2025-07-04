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
    from gioco.oggetto import PozioneCura, Medaglione, BombaAcida
    from copy import deepcopy

    ambiente = session.get('ambiente')
    print(f"DEBUG - ambiente: {ambiente}")
    if isinstance(ambiente, dict):
        ambiente = Ambiente.from_dict(ambiente)
    print(f"DEBUG - ambiente: {ambiente}")

    # Dati base per classi derivate da personaggio
    # (definite in maniera statica per ridurre la complessità del metodo)
    classi_data = {
        'Guerriero': {'at_min': 15, 'att_max_bonus': 20, 'cura_base': 30},
        'Ladro': {'at_min': 5, 'att_max_bonus': 5, 'cura_base': '10-40'},
        'Mago': {'at_min': -5, 'att_max_bonus': 10, 'cura_base': '20%'}
    }

    # Importo dinamico delle classi
    classi_map = {'Mago': Mago, 'Ladro': Ladro, 'Guerriero': Guerriero}
    classi = {nome: classi_map[nome]("temp") for nome in classi_data.keys()}
    oggetti = [PozioneCura(), Medaglione(), BombaAcida()]

    print(f"DEBUG - classi: {classi}")

    # Costruisci valori standard
    val_standard = {}
    for nome, classe in classi.items():
        data = classi_data[nome]
        val_standard[nome] = {
            'attacco': {
                'da': classe.attacco_min + data['at_min'],
                'a': classe.attacco_max + data['att_max_bonus']
            },
            'cura': {'recupero salute': str(data['cura_base'])}
        }

    # Aggiungo gli oggetti al dizionario
    val_standard['Oggetto'] = {
        obj.__class__.__name__: {
            'valore': obj.valore,
            'tipo_oggetto': obj.tipo_oggetto
        } for obj in oggetti
    }

    # Calcola modifiche ambiente
    # (la deepcopy è necessaria per non modificare val_standard)
    var_amb = deepcopy(val_standard)

    for nome, classe in classi.items():
        mod_att = int(ambiente.modifica_attacco(classe))
        mod_cura = int(ambiente.modifica_cura(classe))

        print(f"DEBUG - {nome}: attacco={mod_att}, cura={mod_cura}")

        if mod_att != 0:
            if nome != 'Guerriero':
                var_amb[nome]['attacco']['da'] += mod_att
            var_amb[nome]['attacco']['a'] += mod_att

        if mod_cura != 0:
            segno = '+' if mod_cura > 0 else '-'
            cura_str = {
                'Mago': f"20% (salute rimanente {segno} {abs(mod_cura)})",
                'Ladro': f"da {10 + mod_cura} a {40 + mod_cura}",
                'Guerriero': f"{30 + mod_cura}"
            }
            var_amb[nome]['cura']['recupero salute'] = cura_str[nome]

    # Modifica oggetti
    for obj in oggetti:
        mod_obj = ambiente.modifica_effetto_oggetto(obj)
        if mod_obj != 0:
            var_amb['Oggetto'][obj.__class__.__name__]['valore'] += mod_obj

    print(f"val_standard: {val_standard}")
    print(f"var_amb: {var_amb}")

    return {'val_standard': val_standard, 'var_amb': var_amb}
