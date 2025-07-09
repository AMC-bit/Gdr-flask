import random, logging
from utils.log import Log
from utils.messaggi import Messaggi
from gioco.personaggio import Personaggio

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Mago(Personaggio):
    """
    Classe che rappresenta un personaggio mago.
    Estende la classe personaggio con attacco diminuito e recupero
    di salute personalizzato
    """
    def __init__(self, nome: str, npc: bool = False) -> None:
        """
        Inizializza il personaggio Mago con salute 80

        Args:
            nome (str): nome del personaggio

        Returns:
            None
        """
        super().__init__(nome, npc)
        self.salute = 80

    def attacca(self, mod_ambiente: int = 0) -> None:
        """
        Il Mago ha attacco minimo diminuito di 5 e attacco massimo
        aumentato di 10

        Args:
            bersaglio (Personaggio): personaggio che subisce l'attacco
            mod_ambiente (int): modificatore ambientale di attacco (default: 0)

        Returns:
            int: danno inflitto all'avversario
        """
        danno = random.randint(self.attacco_min - 5, self.attacco_max + 10)
        danno += mod_ambiente
        msg = f"{self.nome} lancia un incantesimo infliggendo {danno} danni!"
        Messaggi.add_to_messaggi(msg)
        Log.scrivi_log(msg)
        return danno

    def recupera_salute(self, mod_ambiente: int = 0) -> None:
        """
        Recupera la salute del Mago alla fine di ogni duello del 20%

        Args:
            mod_ambiente (int): modificatore ambientale di recupero
            (default: 0)

        Returns:
            None
        """
        recupero = int((self.salute + mod_ambiente) * 0.2)
        nuova_salute = min(self.salute + recupero, 80)
        effettivo = nuova_salute - self.salute
        self.salute = nuova_salute
        msg = f"{self.nome} medita e recupera {effettivo} HP." \
            f" Salute attuale: {self.salute}"
        Messaggi.add_to_messaggi(msg)
        Log.scrivi_log(msg)


class Guerriero(Personaggio):
    """
    Classe che rappresenta un personaggio guerriero.
    Estende la classe Personaggio, con salute_max di 120, attacco piu potente e
    guarigione post duello fissa di 30 salute
    """
    def __init__(self, nome: str, npc: bool = False) -> None:
        """
        Inizializza il personaggio Guerriero con salute 120

        Args:
            nome (str): nome del personaggio

        Returns:
            None
        """
        super().__init__(nome, npc)
        self.salute = 120

    def attacca(self, mod_ambiente: int = 0) -> int:
        """
        Il Guerriero ha un attacco minimo aumentato di 15 e un attacco
        massimo aumentato di 20 + il modificatore dell'ambiente corrente

        Args:
            bersaglio (Personaggio): personaggio che subisce l'attacco
            mod_ambiente (int): modificatore ambientale di attacco (default: 0)

        Returns:
            None
        """
        danno = random.randint(
            self.attacco_min + 15,
            self.attacco_max + mod_ambiente + 20
        )
        msg = f"{self.nome} colpisce con la spada infliggendo {danno} danni!"
        Messaggi.add_to_messaggi(msg)
        Log.scrivi_log(msg)
        return danno

    def recupera_salute(self, mod_ambiente: int = 0) -> None:
        """
        Il guerriero al termine di ogni duello recupera salute pari 30

        Args:
            mod_ambiente (int): modificatore ambientale di recupero
            (default: 0)

        Returns:
            None
        """
        recupero = 30 + mod_ambiente
        nuova_salute = min(self.salute + recupero, 120)
        effettivo = nuova_salute - self.salute
        self.salute = nuova_salute
        msg = f"{self.nome} si fascia le ferite e recupera {effettivo} HP." \
            f" Salute attuale: {self.salute}"
        Messaggi.add_to_messaggi(msg)
        Log.scrivi_log(msg)


@dataclass
class Ladro(Personaggio):
    """
    Estende la classe Personaggio, ha salute elevata a 140, +5 attacco_max e
    attacco_min, recupera punti salute al termine del duello
    casualmente in un range 10-40
    """
    salute_max: int = 120
    attacco_max: int = 85
    attacco_min: int = 10

    def __post_init__(self):
        """
        Metodo post-inizializzazione per il Ladro.
        Imposta salute_max a 140 e attacco_min e attacco_max a valori specifici.

        """
        super().__post_init__()
        self.salute = self.salute_max
        self.attacco_max = 85
        self.attacco_min = 10

    def attacca(self, mod_ambiente: int = 0) -> int:
        """
        attacco del ladro valore random tra attacco_min e attacco_max
        con un modificatore ambientale, se l'azione ha successo

        Args:
            mod_ambiente (int): modificatore ambientale di attacco (default: 0)

        Returns:
            danno (int): danno inflitto all'avversario
        """
        danno = 0
        if self.esegui_azione():
            danno = random.randint(
                self.attacco_min, self.attacco_max
            ) + mod_ambiente
            msg = f"{self.nome} colpisce furtivamente infliggendo {danno} danni!"
        else:
            msg = f"{self.nome} tenta di attaccare ma fallisce!"
        logger.info(msg)
        return danno

    def recupera_salute(self, mod_ambiente: int = 0) -> None:
        """
        Permette al ladro di recuperare un numero casuale
        di punti salute in un range 10-40, modificato dall'ambiente

        Args:
            mod_ambiente (int): modificatore ambientale di recupero
            (default: 0)

        Returns:
            None
        """
        recupero = random.randint(10, 40) + mod_ambiente
        nuova_salute = min(self.salute + recupero, 140)
        effettivo = nuova_salute - self.salute
        self.salute = nuova_salute
        msg = f"{self.nome} si cura rapidamente e recupera {effettivo} HP. " \
            f"Salute attuale: {self.salute}"
        logger.info(msg)