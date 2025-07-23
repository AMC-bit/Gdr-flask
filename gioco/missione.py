import uuid
import logging
from dataclasses import dataclass, field
from gioco.personaggio import Personaggio
from gioco.ambiente import Ambiente, AmbienteFactory
from gioco.oggetto import Oggetto
from gioco.inventario import Inventario
from gioco.strategy import Strategia, StrategiaFactory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class Missione():
    """
    Si occupa di aggregare istanze di ambiente , nemici, inventari dei nemici e ricompense
    Rappresenta una missione, composta da un ambiente, nemici e premi.
    """

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    ambiente: Ambiente = field(
        default_factory=lambda: AmbienteFactory.usa_ambiente("Palude")
    )
    nemici: list[Personaggio] = field(default_factory=list)
    #
    inventari_nemici: list[Inventario] = field(default_factory=list)
    premi: list[Oggetto] = field(default_factory=list)
    nome: str = ""
    strategia_nemici: Strategia = field(
        default_factory=lambda: StrategiaFactory.usa_strategia("Equilibrata")
    )
    completata: bool = False
    attiva: bool = False

    def get_nemici(self) -> list[Personaggio]:
        """
        Il metodo deve cercare su static
        Metodo get per ottenere la lista di nemici dentro missione

        Args:
            None

        Returns:
            list[Personaggio] : Ritorna la lista di nemici della Missione

        """
        return self.nemici

    def rimuovi_nemico(self, nemico: Personaggio) -> None:
        """
        Rimuove un nemico dalla lista nemici della Missione
        Args:
        nemico (Personaggio): Nemico da rimuovere dalla lista

        Returns:
            None
        """
        self.nemici.remove(nemico)
        msg = f"{nemico} rimosso dalla lista nemici della missione"
        logger.info(msg)

    def rimuovi_nemici_sconfitti(self) -> None:
        """
        Rimuove i nemici sconfitti dalla proprietà lista nemici

        Args:
            None

        Returns:
            None
        """
        # Metto in una lista i nemici sconfitti che devo rinuovere
        lista_to_remove = []
        for nemico in self.nemici:
            if nemico.sconfitto():
                lista_to_remove.append(nemico)
        # Rimuovo i nemici sconfitti dalla proprietà nemici
        for nemico in lista_to_remove:
            self.rimuovi_nemico(nemico)

    # controlla se la lista self.nemici è vuota e nel caso restituisce True
    def verifica_completamento(self) -> bool:
        """
        Controllo che la lista di nemici sia vuota e in tal caso ritorna True,
        altrimenti False

        Args:
            None

        Returns:
            bool: True se la missione è completata, altrimenti False
        """
        self.rimuovi_nemici_sconfitti()
        if len(self.nemici) == 0:
            self.completata = True
            msg = f"Missione '{self.nome}' completata"
            logger.info(msg)
            return True
        return False
