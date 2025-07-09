import random
import uuid
import logging
from dataclasses import dataclass, field
from marshmallow import Schema, fields, post_load, validate


class PersonaggioSchema(Schema):
    id = fields.Str(dump_only=True)
    nome = fields.Str(required=True, validate=validate.Length(min=4))
    classe = fields.Str(required=True)
    salute = fields.Int(required=True, validate=validate.Range(min=-1, max=120))
    livello = fields.Int(required=True, validate=validate.Range(min=0))
    destrezza = fields.Int(required=True, validate=validate.Range(min=0))
    storico_danni_subiti = fields.List(fields.Int())

logger = logging.getLogger(__name__)
# - Ogni logger del logging ha un livello di soglia ed i messaggi vengono
# inviati solo le il livello è maggiore di quello di soglia
# - Livelli standard in ordine: DEBUG INFO WARNING ERROR CRITICAL
# - Quindi facendo logger.setlevel(logging.info) i messaggi di livello
# inferiore ad info vengono ignorati
# - In produzione si alza la soglia almeno a WARNING in modo da non intasare
# il log con troppi messaggi
# - Questo non verrà mai mostrato, perché è di livello DEBUG < INFO
# logger.debug("Questo è un messaggio di debug e verrà ignorato")
# - Questo verrà mostrato, perché è di livello INFO >= INFO
# logger.info("Questo è un messaggio di info e verrà registrato")
# - Si possono loggare i warning con 'import warnings' e con
# logging.captureWarnings(True)
logger.setLevel(logging.INFO)


@dataclass
class Personaggio:
    """
    Classe Padre per tutte classi
    Contiene le proprietà comuni a ogni classe (Mago, Ladro, Guerriero)
    """

    # - In una @dataclass i campi possono avere un dato di default oppure
    # possono avere dei dati calcolati al momento della creazione dell'istanza,
    # tramite default_factory
    # - Lambda è una funzione anonima che viene chiamata nel momento di
    # creazione di un nuovo oggetto, in modo da generare il valore
    # di default del campo id
    # - Default_factory in pratica garantisce che ogni istanza
    # abbia un proprio UUID unico, senza doverlo passare manualmente
    # al costruttore
    # - Evita il problema di valori mutabili di default condivisi tra
    # tutte le istanze, come succederebbe con una lista definita direttamente
    nome: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    npc: bool = True
    salute: int = 100
    salute_max: int = 200
    attacco_min: int = 5
    attacco_max: int = 80
    storico_danni_subiti: list[int] = field(default_factory=list)
    # - Se avessimo scritto storico_danni_subiti: list[int] = []
    # questo elenco verrebbe generato una sola volta e condivisa tra
    # tutte le istanze di Personaggio
    # - Invece usando default_factory=list il dataclass chiama list() ogni
    # volta che si crea un nuovo oggetto forneno a ciascuna istanza la
    # propria lista vuota indipendente
    livello: int = 1
    destrezza: int = 15
    classe: str = field(init=False)

    def __post_init__(self):
        self.classe = self.__class__.__name__

    def esegui_azione(self) -> bool:
        """
        Tira un d20 e verifica se il risultato è minore o uguale alla destrezza del personaggio.

        Returns:
            bool: True se il testo è superato, False altrimenti.
        """
        tiro = random.randint(1, 20)
        successo = tiro <= self.destrezza
        if successo:
            logger.info(f"{self.nome} ha eseguito l'azione con successo! (tiro={tiro})")
        else:
            logger.info(f"{self.nome} ha fallito l'azione! (tiro={tiro})")
        return successo

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
        if not self.esegui_azione():
            logger.info(f"{self.nome} Tenta di attaccare ma fallisce!")
            return 0
        danno = random.randint(self.attacco_min, self.attacco_max) + mod_ambiente
        logger.info(f"{self.nome} Attacca con successo e infligge {danno} danni!")
        return danno

    def subisci_danno(self, danno: int) -> None:
        """
        Sottrae il danno (Input) alla salute del personaggio.

        Args:
            danno (int): danno subito dal personaggio

        Returns:
            None
        """
        self.salute = max(0, self.salute - danno)
        self.storico_danni_subiti.append(danno)
        logger.info(f"Salute di {self.nome}: {self.salute} (danni subiti: {danno}")

    def sconfitto(self) -> bool:
        """
        Verifica se il personaggio è sceso a zero di salute.

        Args:
            None

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

        Returns:
            None
        """
        if self.salute >= self.salute_max:
            logger.info(f"{self.nome} ha già la salute piena.")
            return
        recupero = int(self.salute * 0.3) + mod_ambiente
        nuova_salute = min(self.salute + recupero, 100)
        effettivo = nuova_salute - self.salute
        self.salute = nuova_salute
        logger.info(
            f"\n{self.nome} recupera {effettivo} HP. Salute attuale: {self.salute}/{self.salute_max}"
            )

    def migliora_statistiche(self) -> None:
        """
        Metodo per aumentare il livello del personaggio e quindi
        migliorarne le statistiche.
        Aumenta del 2% l'attacco massimo e dell'1% la salute massima.

        Args:
            None

        Returns:
            None
        """
        self.livello += 1
        self.attacco_max = int(self.attacco_max + 0.02 * self.attacco_max)
        self.salute_max = int(self.salute_max + 0.01 * self.salute_max)
        logger.info(f"{self.nome} è salito al livello {self.livello}!")