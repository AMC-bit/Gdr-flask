from . import characters_bp
from flask import render_template, request, redirect, url_for, session, abort
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
        inv = Inventario(proprietario=pg.id)
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

# Route per visualizzare la lista dei personaggi
@characters_bp.route('/personaggi', methods=['GET', 'POST'])
def mostra_personaggi():
    lista_pers = session.get('personaggi', [])
    return render_template('list_char.html', personaggi=lista_pers)

# Route per visualizzare un personaggio singolo tramite indice
@characters_bp.route('/personaggi/<int:id>')
def dettaglio_personaggio(id):
    lista_pers = session.get('personaggi', [])
    try:
        pg = lista_pers[id]
    except IndexError:
        abort(404)
    return render_template('details_char.html', pg=pg, id=id)

# Route per eliminare un personaggio (usando indice)
@characters_bp.route('/personaggi/<int:id>', methods=['POST'])
def elimina_personaggio(id):
    lista_pers = session.get('personaggi', [])
    try:
        for pg in lista_pers:
            if pg['id'] == id:
                lista_pers.remove(pg)
            return redirect(url_for('characters.mostra_personaggi'))
    except IndexError:
        abort(404)
    return redirect(url_for('characters.mostra_personaggi'))

