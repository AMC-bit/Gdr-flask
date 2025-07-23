import random, logging
from gioco.ambiente import Ambiente
from gioco.inventario import Inventario
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class Strategia ():
    '''
    La classe Strategia è una classe base per le strategie di attacco
    degli NPC (non-player-character, personaggio non giocabile).
    Ogni strategia di attacco deve derivare da questa classe e implementare il
    metodo uso_inventario_npc.
    '''
    nome: str = "Strategia di attacco"
    def __init__(self):
        msg = "Attenzione! le classi da utilizzare sono le classi derivate!"
        logger.warning(msg)

    @staticmethod
    def uso_inventario_npc(
        salute_npc: int,
        inventario: 'Inventario',
        ambiente: 'Ambiente' = None,
    ) -> int | None:
        '''
        viene definito un metodo astratto che deve essere implementato
        dalle classi derivate.

        Args:
            salute_npc (int): la salute del NPC
            inventario (Inventario): l'inventario del NPC
            ambiente (Ambiente): l'ambiente di gioco (opzionale)

        Returns:
            int | None: il risultato dell'attacco, che può essere un intero
            rappresentante i danni inflitti o None se non viene utilizzato
            nessun oggetto

        Raises:
            NotImplementedError: il metodo è implementato nelle classi
            derivate.
        '''
        raise NotImplementedError(
            "Devi implementare il metodo esegui nella sottoclasse"
        )


'''
le classi si occuperanno di gestire le decisioni del NPC
durante il suo turno
'''


@dataclass
class Aggressiva(Strategia):
    '''
    la classe Aggressiva rappresenta una strategia in cui l'NPC decide di
    focalizzarsi sul fare il maggior danno possibile alla salute del bersaglio.
    '''
    nome: str = "Aggressiva"
    def __init__(self):
        msg = (
            "Il NPC ha scelto una strategia aggressiva! "
            "Attaccherà con tutte le sue forze!"
        )
        logger.info(msg)

    @staticmethod
    def uso_inventario_npc(
        salute_npc: int,
        inventario: Inventario,
        ambiente: Ambiente = None
    ) -> int | bool:
        '''
        Esegue l'attacco aggressivo del NPC sul bersaglio. l'unico oggetto
        che può essere usato è la Bomba Acida, che infligge danni al bersaglio.

        args:
            inventario (Inventario): l'inventario del NPC
            ambiente (Ambiente): l'ambiente di gioco (opzionale)
        Returns:
            Nessuno
        '''
        result = None
        if inventario and inventario.oggetti:
            ogg = next(
                (
                    ogg for ogg in inventario.oggetti
                    if ogg.nome == "Bomba Acida"
                ),
                None
            )
            if ogg and (random.randint(0, 1) == 0):
                result = inventario.usa_oggetto(
                    oggetto=ogg,
                    ambiente=ambiente
                )
        return result



@dataclass
class Difensiva(Strategia):
    '''
    La classe Difensiva rappresenta una strategia in cui il NPC si concentra
    sulla propria salute, curandosi quando questa è sotto i 60 punti e
    attaccando il bersaglio altrimenti.
    '''
    nome: str = "Difensiva"
    def __init__(self):
        msg = "Il NPC ha scelto una strategia difensiva! "
        logger.info(msg)

    @staticmethod
    def uso_inventario_npc(
        salute_npc: int,
        inventario: 'Inventario',
        ambiente: 'Ambiente' = None
    ) -> None:
        '''
        Esegue l'attacco difensivo del NPC sul bersaglio.
        Se la salute del personaggio non giocante (npc) è inferiore a 60 punti, usa una Pozione Rossa
        per curarsi e poi attacca il bersaglio, altrimenti attacca soltanto.
        La probabilità di usare la Pozione Rossa è randomica,
        con una probabilità del 50%.

        Args:
            salute_npc (int): la salute del NPC
            inventario (Inventario): l'inventario del NPC
            ambiente (Ambiente): l'ambiente di gioco (opzionale)

        Returns:
            None

        '''
        result = None
        if salute_npc < 60 and inventario and inventario.oggetti:
            ogg = next(
                (
                    ogg for ogg in inventario.oggetti
                    if ogg.nome == "Pozione Rossa"
                ),
                None
            )
            if ogg and (random.randint(0, 1) == 0):
                result = inventario.usa_oggetto(
                    oggetto=ogg,
                    ambiente=ambiente
            )
        return result


class Equilibrata(Strategia):
    '''
    La classe Equilibrata rappresenta una strategia in cui il NPC decide di
    curarsi quando la salute è sotto i 40 punti, altrimenti di usare una bomba
    acida e infine attaccare il bersaglio
    l'uso degli oggetti è randomico.
    '''
    nome: str = "Equilibrata"
    def __init__(self):
        msg = (
            " il NPC ha scelto una strategia equilibrata! "
        )
        logger.info(msg)

    @staticmethod
    def uso_inventario_npc(
        salute_npc: int,
        inventario: 'Inventario',
        ambiente: 'Ambiente' = None
    ) -> int | None:
        '''

        Esegue l'attacco equilibrato del NPC sul bersaglio. Se la salute
        del NPC è inferiore a 40 punti, usa una Pozione Rossa per curarsi e
        poi attacca il bersaglio, altrimenti usa una Bomba Acida per infliggere
        danni al bersaglio e poi attacca.
        L'uso degli oggetti avviene in modo randomico, con una probabilità del
        33% per ciascun oggetto.

        Args:
            NPC (Personaggio): il NPC che esegue l'attacco
            bersaglio (Personaggio): il bersaglio dell'attacco
            inventario (Inventario): l'inventario del NPC
            ambiente (Ambiente): l'ambiente di gioco (opzionale)

        Returns:
            int | None: il risultato dell'azione, che può essere un intero
            rappresentante i danni inflitti o None se non viene effettuato
        '''
        result = None
        msg = ""
        if salute_npc < 40:
            if inventario and inventario.oggetti:
                ogg = next(
                    (
                        ogg for ogg in inventario.oggetti
                        if ogg.nome == "Pozione Rossa"
                    ),
                    None
                )
                if ogg and (random.randint(0, 2) == 0):
                    result = inventario.usa_oggetto(
                        oggetto=ogg,
                        ambiente=ambiente
                    )
                    msg = (
                        "viene usata una Pozione Rossa per curarsi di "
                        f"{result} punti ferita")
        elif inventario and inventario.oggetti:
            ogg = next(
                (
                    ogg for ogg in inventario.oggetti
                    if ogg.nome == "Bomba Acida"
                ),
                None
            )
            if ogg and (random.randint(0, 2) == 0):
                result = inventario.usa_oggetto(
                    ogg,
                    ambiente=ambiente
                )
                msg = (
                    "viene utilizzata una Bomba Acida causando un danno di "
                    f"{result} punti ferita"
                )
        if msg != "":
            logger.info(msg)
        return result

# ----------------------------------------------------------------------------


class StrategiaFactory:
    @staticmethod
    def usa_strategia(tipo: str) -> Strategia:
        '''
        Restituisce un'istanza della strategia richiesta in base
        al tipo passato come argomento.

        Args:
            tipo (str): il tipo di strategia da utilizzare
                può essere "aggressiva", "difensiva" o "equilibrata".

        Returns:
            Strategia: un'istanza della strategia richiesta.

        Raises:
            ValueError: se il tipo di strategia non è valido.
        '''
        tipo = tipo.lower()
        if tipo == "aggressiva":
            return Aggressiva()
        elif tipo == "difensiva":
            return Difensiva()
        elif tipo == "equilibrata":
            return Equilibrata()
        else:
            raise ValueError(f"Tipo di strategia sconosciuto: {tipo}")



