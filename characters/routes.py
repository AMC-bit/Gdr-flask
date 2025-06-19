from . import characters_bp
from flask import render_template, request, redirect, url_for, session
from gioco.personaggio import Personaggio
from gioco.classi import Mago, Guerriero, Ladro
from gioco.oggetto import PozioneCura, BombaAcida, Medaglione
from gioco.inventario import Inventario

# mappa dinamica delle classi disponibili
CLASSI = {
    'Mago': Mago,
    'Guerriero': Guerriero,
    'Ladro': Ladro
}
# mappa dinamica degli oggetti disponibili
OGGETTI = {
    'Pozione Rossa': PozioneCura,
    'Bomba Acida': BombaAcida,
    'Medaglione': Medaglione
}


@characters_bp.route('/create_char', methods=['GET','POST'])
def create_char():
    if request.method == 'POST':

        # prendo i dati dal form
        nome = request.form['nome'].strip()
        classe_sel = request.form['classe']
        oggetto_sel = request.form['oggetto']

        # istanziamento personaggio, oggetto e inventario
        pg = CLASSI[classe_sel](nome)
        ogg = OGGETTI[oggetto_sel]()
        inv = Inventario(proprietario=pg)
        inv.aggiungi_oggetto(ogg)

        # prendo o inizializzo le due liste
        pg_list = session.get('personaggi', [])
        inv_list = session.get('inventari',  [])

        # aggiungo i nuovi dizionari alle liste
        pg_list.append(pg.to_dict())
        inv_list.append(inv.to_dict())

        # riassegno alle chiavi di sessione le liste aggiornate
        session['personaggi'] = pg_list
        session['inventari']   = inv_list

        # redirect al menu principale
        return redirect(url_for('gioco.index'))

    return render_template(
        'create_char.html',
        classi=list(CLASSI.keys()),
        oggetti=list(OGGETTI.keys())
    )


@characters_bp.route('/debug')
def debug():
    print("sessione:", dict(session))
    return 'debug completato'


@characters_bp.route('/view_characters')
def view_characters():    
    return render_template('view_characters.html')

