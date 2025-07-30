import uuid
from utils.log import get_logger
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

logger = get_logger(__name__)

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
        """ Ritorna la lista dei nemici della missione.

        Returns:
            List[Personaggio]: Lista dei nemici presenti nella missione.
        """
        return self.nemici

    def rimuovi_nemico(self, nemico: Personaggio) -> None:
        """ Rimuove un nemico dalla lista dei nemici della missione.

        Args:
            nemico (Personaggio): Il nemico da rimuovere dalla missione.
        """
        if nemico in self.nemici:
            self.nemici.remove(nemico)
            logger.info(f"{nemico.nome} rimosso dai nemici della missione.")

    def rimuovi_nemici_sconfitti(self) -> None:
        """ Rimuove i nemici sconfitti dalla lista dei nemici della missione."""
        nemici_vivi = [n for n in self.nemici if not n.sconfitto()]
        rimossi = [n for n in self.nemici if n.sconfitto()]
        self.nemici = nemici_vivi
        for nemico in rimossi:
            logger.info(f"{nemico.nome} (sconfitto) rimosso dalla missione.")

    def verifica_completamento(self) -> bool:
        """ Verifica se la missione è completata. Se non ci sono nemici rimasti, la missione è completata.

        Returns:
            bool: True se la missione è completata, False altrimenti.
        """
        self.rimuovi_nemici_sconfitti()
        if not self.nemici:
            self.completata = True
            logger.info(f"Missione '{self.nome}' completata!")
            return True
        return False
