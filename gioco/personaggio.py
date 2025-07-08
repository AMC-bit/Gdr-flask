import random, uuid, logging
from dataclasses import dataclass, field
from gioco.basic import Basic
from marshmallow import Schema, fields, post_load

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# ogni logger del logging ha un livello di soglia ed i messaggi vengono inviati
# solo se il livello è maggiore di quello di soglia
# i livelli standard (in ordine crescente di gravità): DEBUG, INFO, ERROR, CRITICAL
# quindi facendo logger.setLevel(logging.INFO) i messaggi di livello inferiore
# ad info vengono ignorati
# in produzione si alza la soglia almeno a warning in modo da non intasare il
# log con troppi messaggi


@dataclass
class Personaggio():
    """
    Classe Padre per tutte classi
    Contiene le proprietà comuni a ogni classe (Mago, Ladro, Guerriero)
    """
    nome: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    npc: bool = True
    salute: int = 100
    salute_max: int = 200
    attacco_min: int = 5
    attacco_max: int = 80
    storico_danni_subiti: list[int] = field(default_factory=list)
    livello: int = 1
    destrezza: int = 15
    classe: str = field(init=False)
    """
        in una @dataclass i campi possono avere un dato di default oppure
        possono avere dei dati calcolati al momento della creazione
        dell'istanza, tramite default_factory
        lambda è una funzione anonima che viene chiamata al momento della
        creazione di un nuovo oggetto in modo da generare il valore di default
        del campo id
        default_factory in pratica garantisce che ogni istanza abbia un
        proprio UUID unico, senza doverlo passare manualmente al costruttore
        Evita il problema di valori mutabili di default condivisi tra tutte
        le istanze (come succederebbe con una lista definita direttamente)
    """
    def __post_init__(self):
        """
        Metodo chiamato automaticamente dopo la creazione dell'istanza.
        Imposta il nome della classe come valore del campo 'classe'.
        """
        self.classe = self.__class__.__name__

    # def __init__(self, nome: str, npc: bool = True) -> None:
        # self.id = str(uuid.uuid4())
        # self.nome = nome
        # self.salute = 100
        # self.salute_max = 200
        # self.attacco_min = 5
        # self.attacco_max = 80
        # self.storico_danni_subiti = []
        # self.livello = 1
        # self.destrezza = 15  # Caratteristica per la sistema d20
        # self.npc = npc  # Indica se il personaggio è un NPC

    def esegui_azione(self) -> bool:
        """
        Tira un d20 e verifica se il risultato è minore o uguale alla destrezza del personaggio.

        Returns:
            bool: True se il testo è superato, False altrimenti.
        """
        tiro = random.randint(1, 20)
        risultato = tiro <= self.destrezza
        if risultato:
            msg = f"{self.nome} ha eseguito l'azione con successo! (tiro={tiro})"
            logger.info(msg)
        else:
            msg = f"{self.nome} ha fallito l'azione! (tiro={tiro})"
            logger.info(msg)
        return risultato

    def attacca(self, mod_ambiente: int = 0) -> int:
        """
        Tenta un attacco generando un danno casuale tra attacco_min e attacco_max,
        influenzato da eventuali modificatori ambientali. Il successo dipende da un tiro
        basato sulla destrezza (sistama d20).

        Args:
            mod_ambiente (int): modificatore di attacco in base all'ambiente

        Returns:
            int: danno inflitto all'avversario, 0 se l'attacco fallisce
        """
        if self.esegui_azione():
            danno = random.randint(self.attacco_min, self.attacco_max) + mod_ambiente
            msg = f"{self.nome} Attacca con successo e infligge {danno} danni!"
            logger.info(msg)
            return danno
        msg = f"{self.nome} Tenta di attaccare ma fallisce!"
        logger.info(msg)
        return 0

    def subisci_danno(self, danno: int) -> None:
        """
        Sottrae il danno (Input) alla salute del personaggio.
        Args:
            danno (int): danno subito dal personaggio
        """
        self.salute = max(0, self.salute - danno)
        self.storico_danni_subiti.append(danno)
        msg = f"Salute di {self.nome}: {self.salute}\n"
        logger.info(msg)

    def sconfitto(self) -> bool:
        """
        Verifica se il personaggio è sceso a zero di salute.
        Returns:
            bool: True se il personaggio è sconfitto, in caso contrario False
        """
        return self.salute <= 0

    def recupera_salute(self, mod_ambiente: int = 0) -> None:
        """
        Recupera la salute del personaggio del 30% della salute corrente.
        Viene usato da pozioni e dal recupero salute post duello.

        Args:
            mod_ambiente (int): modificatore di recupero in base all'ambiente
        """
        if self.salute >= self.salute_max:
            msg = f"{self.nome} ha già la salute piena."
            logger.info(msg)
            return
        recupero = int(self.salute * 0.3) + mod_ambiente
        nuova_salute = min(self.salute + recupero, 100)
        effettivo = nuova_salute - self.salute
        self.salute = nuova_salute
        msg = f"\n{self.nome} recupera {effettivo} HP. Salute attuale: {self.salute}"
        logger.info(msg)

    def migliora_statistiche(self) -> None:
        """
        Metodo per aumentare il livello del personaggio e quindi
        migliorarne le statistiche.
        Aumenta del 2% l'attacco massimo e dell'1% la salute massima.
        """
        self.livello += 1
        self.attacco_max = int(self.attacco_max + 0.02 * self.attacco_max)
        self.salute_max = int(self.salute_max + 0.01 * self.salute_max)
        msg = f"{self.nome} è salito al livello {self.livello}!"
        logger.info(msg)

"""
    def to_dict(self) -> dict:
        "" "Restituisce uno stato serializzabile per session o JSON.

        Returns:
            dict: Dizionario del materiale serializzato
        "" "
        return {
            "classe": self.__class__.__name__,
            "id": self.id,
            "nome": self.nome,
            "salute": self.salute,
            "salute_max": self.salute_max,
            "attacco_min": self.attacco_min,
            "attacco_max": self.attacco_max,
            "storico_danni_subiti": self.storico_danni_subiti,
            "livello": self.livello,
            "destrezza": self.destrezza,
            "npc": self.npc
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Personaggio":
        "" "Ricostruisce l’istanza a partire da un dict serializzato.

        Args:
            data (dict): Dati serializzati

        Returns:
            Personaggio: Dati deserializzati
        "" "
        obj = cls(data["nome"])
        obj.id = data.get('id')
        obj.salute = data.get("salute", 100)
        obj.salute_max = data.get("salute_max", 200)
        obj.attacco_min = data.get("attacco_min", 5)
        obj.attacco_max = data.get("attacco_max", 80)
        obj.storico_danni_subiti = data.get("storico_danni_subiti", [])
        obj.livello = data.get("livello", 1)
        obj.destrezza = data.get("destrezza", 15)
        obj.npc = data.get("npc", True)
        return obj
 """
