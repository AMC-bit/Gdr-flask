from gioco.personaggio import Personaggio
from gioco.classi import Mago, Guerriero, Ladro

@staticmethod
def credits_for_char(personaggio: Personaggio) -> int:
    """
    Questa funzione permette di restituire il numero di crediti necessari per creare un personaggio
    oppure il numero di crediti restituiti nel caso in cui l'utente decide di cancellare un personaggio.
    Il valore restituito dalla funzione varia a secondo della classe del personaggio.

    Args:
        Personaggio(Personaggio): oggetto personaggio di cui vogliamo calcolare i crediti necessari
        per la sua creazione, oppure restituiti per la sua cancellazione.

    return:
        credits_char(int): valore dei crediti sostrati per la creazione del personaggio oppure restituiti
        per la cancellazione del personaggio
    """
    credits_char = 0
    if personaggio.classe == "Mago":
        credits_char = 20
        return credits_char
    elif personaggio.classe == "Guerriero":
        credits_char = 30
        return credits_char
    elif personaggio.classe == "Ladro":
        credits_char = 50
        return credits_char
    else:
        msg = f"Il personaggio {personaggio} selezionato non è valido."