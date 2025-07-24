import random
import uuid
import logging
from dataclasses import dataclass, field
from typing import List
from gioco.personaggio import Personaggio
from gioco.ambiente import Ambiente, AmbienteFactory
from gioco.oggetto import Oggetto
from gioco.inventario import Inventario
from gioco.strategy import Strategia, StrategiaFactory

'''
1- Logger
2 - Modificato nemici sconfitti adesso dovrebbe funzionare senza bug
'''

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class Missione:
    """
    Aggrega ambiente, nemici, inventari nemici e premi.
    Rappresenta una missione, composta da un ambiente, nemici e premi.
    """
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    ambiente: Ambiente = field(default_factory=lambda: AmbienteFactory.usa_ambiente("Palude"))
    nemici: List[Personaggio] = field(default_factory=list)
    inventari_nemici: List[Inventario] = field(default_factory=list)
    premi: List[Oggetto] = field(default_factory=list)
    nome: str = ""
    strategia_nemici: Strategia = field(default_factory=lambda: StrategiaFactory.usa_strategia("Equilibrata"))
    completata: bool = False
    attiva: bool = False

    def get_nemici(self) -> List[Personaggio]:
        """Restituisce la lista dei nemici attuali."""
        return self.nemici

    def rimuovi_nemico(self, nemico: Personaggio) -> None:
        """Rimuove un nemico dalla lista."""
        if nemico in self.nemici:
            self.nemici.remove(nemico)
            logger.info(f"{nemico.nome} rimosso dai nemici della missione.")

    def rimuovi_nemici_sconfitti(self) -> None:
        """Rimuove tutti i nemici sconfitti dalla lista."""
        nemici_vivi = [n for n in self.nemici if not n.sconfitto()]
        rimossi = [n for n in self.nemici if n.sconfitto()]
        self.nemici = nemici_vivi
        for nemico in rimossi:
            logger.info(f"{nemico.nome} (sconfitto) rimosso dalla missione.")

    def verifica_completamento(self) -> bool:
        """
        True se tutti i nemici sono sconfitti (lista vuota).
        """
        self.rimuovi_nemici_sconfitti()
        if not self.nemici:
            self.completata = True
            logger.info(f"Missione '{self.nome}' completata!")
            return True
        return False

    def assegna_premio(self, inventari_giocatori: List[Inventario]) -> None:
        """
        Assegna gli oggetti premio agli inventari dei giocatori, distribuendo casualmente.
        """
        if not inventari_giocatori:
            logger.warning("Nessun inventario per assegnare premi.")
            return

        for premio in self.premi:
            inventario = random.choice(inventari_giocatori)
            if getattr(inventario, "id_proprietario", None) is None:
                msg = "Non è possibile assegnare un premio a un inventario senza proprietario!"
                logger.warning(msg)
                raise ValueError(msg)
            inventario._aggiungi(premio)  # O il tuo metodo pubblico
            logger.info(f"Premio '{premio.nome}' aggiunto all'inventario di {inventario.id_proprietario}")

    def verifica_e_assegna_premi(self, inventari_vincitori: List[Inventario]) -> bool:
        """
        Esegue la verifica completamento missione e, se completata, assegna i premi.
        Returns True se completata e premi assegnati.
        """
        self.rimuovi_nemici_sconfitti()
        if self.verifica_completamento():
            self.assegna_premio(inventari_vincitori)
            return True
        return False
