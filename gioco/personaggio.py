from dataclasses import dataclass, field
import uuid
import random
from utils.log import get_logger

'''
1- La logica di attacca o recupera_salute nelle sottoclassi cambia solo un dettaglio, lasciando intatto il comportamento principale
Quindi conviene usare super() per richiamare la logica di base e poi modificare solo il messaggio o il calcolo del danno.

2- Il calcolo del danno è separato in un metodo calcola_danno, che può essere personalizzato dalle sottoclassi
per cambiare il modo in cui viene calcolato il danno, ma mantiene la logica di base di Personaggio.
Override completo se la logica della classe figlia è molto diversa (es. ladro recupera in modo casuale, mago percentuale diversa, ecc.)

3 - Costanti sempre coerenti usando properties della classe Personaggio

4 - logger in un file separato con una sola configurazione centralizzata, personalizzabile facilmente, senza duplicare codice in ogni modulo
name serve per avere il nome del modulo che usa il logger (__name__)
level puo essere messo a WARNING per la produzione
logger = get_logger(__name__)
logger.info("Questo è un messaggio di info!")
logger.warning("Attenzione, qualcosa non va!")
logger.error("Errore grave!")
'''

logger = get_logger(__name__)

@dataclass
class Personaggio:
    nome: str = ""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    npc: bool = True
    salute: int = 100
    salute_max: int = 200
    attacco_min: int = 5
    attacco_max: int = 80
    storico_danni_subiti: list[int] = field(default_factory=list)
    livello: int = 1
    destrezza: int = 15
    iniziativa: int = 0
    classe: str = ""

    def esegui_azione(self) -> bool:
        tiro = random.randint(1, 20)
        successo = tiro <= self.destrezza
        msg = (
            f"{self.nome} ha eseguito l'azione con successo! (tiro={tiro})"
            if successo else
            f"{self.nome} ha fallito l'azione! (tiro={tiro})"
        )
        logger.info(msg)
        return successo

    def calcola_danno(self, mod_ambiente: int = 0) -> int:
        """Metodo separato per il calcolo del danno, personalizzabile dalle sottoclassi."""
        return random.randint(self.attacco_min, self.attacco_max) + mod_ambiente

    def attacca(self, mod_ambiente: int = 0) -> tuple[int, str]:
        if self.esegui_azione():
            danno = max(0, self.calcola_danno(mod_ambiente))
            msg = (
                f"{self.nome} attacca e infligge {danno} danni!"
                if danno > 0
                else f"{self.nome} attacca ma non infligge danni!"
            )
        else:
            danno = 0
            msg = f"{self.nome} tenta di attaccare ma fallisce!"
        logger.info(msg)
        return danno, msg

    def subisci_danno(self, danno: int) -> None:
        self.salute = max(0, self.salute - danno)
        self.storico_danni_subiti.append(danno)
        logger.info(f"Salute di {self.nome}: {self.salute}")

    def sconfitto(self) -> bool:
        return self.salute <= 0


    def migliora_statistiche(self) -> None:
        self.livello += 1
        self.attacco_max = int(self.attacco_max * 1.02)
        self.salute_max = int(self.salute_max * 1.01)
        logger.info(f"{self.nome} è salito al livello {self.livello}!")


@dataclass
class Mago(Personaggio):
    salute_max: int = 80
    salute: int = 80
    attacco_min: int = 0
    attacco_max: int = 90
    iniziativa: int = 15
    classe: str = "Mago"

    def calcola_danno(self, mod_ambiente: int = 0) -> int:
        # Calcolo danno personalizzato che estende la logica di personaggio
        return random.randint(self.attacco_min, self.attacco_max) + mod_ambiente

    def attacca(self, mod_ambiente: int = 0) -> tuple[int, str]:
        danno, _ = super().attacca(mod_ambiente)
        # Cambia solo il messaggio, non la logica
        if danno > 0:
            msg = f"{self.nome} lancia un incantesimo infliggendo {danno} danni!"
        else:
            msg = f"{self.nome} lancia un incantesimo, ma non infligge danni!"
        logger.info(msg)
        return danno, msg

    def recupera_salute(self, mod_ambiente: int = 0) -> str:
        # Cambia solo la percentuale di recupero (20%)
        if self.salute >= self.salute_max:
            msg = f"{self.nome} ha già la salute piena."
        else:
            recupero = int((self.salute + mod_ambiente) * 0.2)
            nuova_salute = min(self.salute + recupero, self.salute_max)
            effettivo = nuova_salute - self.salute
            self.salute = nuova_salute
            msg = f"{self.nome} medita e recupera {effettivo} HP. Salute attuale: {self.salute}"
        logger.info(msg)
        return msg


@dataclass
class Guerriero(Personaggio):
    salute_max: int = 130
    salute: int = 130
    attacco_min: int = 20
    attacco_max: int = 100
    iniziativa: int = 20
    classe: str = "Guerriero"

    def attacca(self, mod_ambiente: int = 0) -> tuple[int, str]:
        danno, _ = super().attacca(mod_ambiente)
        if danno > 0:
            msg = f"{self.nome} colpisce con la spada infliggendo {danno} danni!"
        else:
            msg = f"{self.nome} colpisce, ma non infligge danni!"
        logger.info(msg)
        return danno, msg

    def recupera_salute(self, mod_ambiente: int = 0) -> str:
        # Recupero fisso di 30
        if self.salute >= self.salute_max:
            msg = f"{self.nome} ha già la salute piena."
        else:
            recupero = 30 + mod_ambiente
            nuova_salute = min(self.salute + recupero, self.salute_max)
            effettivo = nuova_salute - self.salute
            self.salute = nuova_salute
            msg = f"{self.nome} si fascia le ferite e recupera {effettivo} HP. Salute attuale: {self.salute}"
        logger.info(msg)
        return msg


@dataclass
class Ladro(Personaggio):
    salute_max: int = 120
    salute: int = 120
    attacco_min: int = 10
    attacco_max: int = 85
    iniziativa: int = 25
    classe: str = "Ladro"

    def attacca(self, mod_ambiente: int = 0) -> tuple[int, str]:
        danno, _ = super().attacca(mod_ambiente)
        if danno > 0:
            msg = f"{self.nome} colpisce furtivamente infliggendo {danno} danni!"
        else:
            msg = f"{self.nome} colpisce, ma non infligge danni!"
        logger.info(msg)
        return danno, msg

    def recupera_salute(self, mod_ambiente: int = 0) -> str:
        # Recupero casuale tra 10-40 (+ mod_ambiente)
        if self.salute >= 140:
            msg = f"{self.nome} ha già la salute piena."
        else:
            recupero = random.randint(10, 40) + mod_ambiente
            nuova_salute = min(self.salute + recupero, 140)
            effettivo = nuova_salute - self.salute
            self.salute = nuova_salute
            msg = f"{self.nome} si cura rapidamente e recupera {effettivo} HP. Salute attuale: {self.salute}"
        logger.info(msg)
        return msg
