from gioco.personaggio import Personaggio
from gioco.classi import Mago, Guerriero, Ladro

@staticmethod
def credits_to_create(personaggio: Personaggio) -> int:
    """
    Restituisce il numero di crediti necessari per creare un personaggio.
    I costi cambiano a secondo della classe del personaggio che si vuole creare.
    ("Mago" costa 20 crediti, "Guerriero" 25 crediti, "Ladro" 50 crediti)

    Args:
        personaggio (Personaggio): oggetto della classe Personaggio

    Returns:
        int: crediti necessari alla creazione del personaggio
    """
    classe = personaggio.__class__.__name__
    if classe == "Mago":
        return 2
    elif classe == "Guerriero":
        return 5
    elif classe == "Ladro":
        return 7
    else:
        raise ValueError(f"Classe del personaggio non riconosciuta.")


@staticmethod
def credits_to_refund(personaggio: Personaggio) -> int:
    """
    Restituisce il numero di crediti rimborsati all'utente in caso di cancellazione
    del personaggio. Il rimborso è un valore fisso in base alla classe del personaggio.

    ("Mago" rimborsa 10 crediti, "Guerriero" 12 crediti, "Ladro" 25 crediti)

    Args:
        personaggio (Personaggio): oggetto della classe Personaggio

    Returns:
        int: crediti rimborsati all'utente
    """
    # pg_dict = personaggio.to_dict()
    # classe = pg_dict['classe']
    classe = personaggio.__class__.__name__
    if classe == "Mago":
        return 2
    elif classe == "Guerriero":
        return 5
    elif classe == "Ladro":
        return 7
    else:
        raise ValueError(f"Classe del personaggio non riconosciuta.")
