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
    if personaggio.__class__.__name__ == "Mago":
        return 20
    elif personaggio.__class__.__name__ == "Guerriero":
        return 25
    elif personaggio.__class__.__name__ == "Ladro":
        return 50
    else:
        raise ValueError(f"Classe '{personaggio.__class__.__name__}' non riconosciuta.")


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
    if personaggio.__class__.__name__ == "Mago":
        return 10
    elif personaggio.__class__.__name__ == "Guerriero":
        return 12
    elif personaggio.__class__.__name__ == "Ladro":
        return 25
    else:
        raise ValueError(f"Classe '{personaggio.__class__.__name__}' non riconosciuta.")
