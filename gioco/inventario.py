import uuid
from utils.log import get_logger
from gioco.oggetto import Oggetto
from gioco.ambiente import Ambiente
from typing import List, Optional, Union
from dataclasses import dataclass, field


'''
1- Logger
2- Rimozione oggetto via id Cerca oggetto sia per nome che per id
'''
logger = get_logger(__name__)

@dataclass
class Inventario:
    """Gestisce la lista di oggetti posseduti da ogni personaggio."""
    id_proprietario: Optional[uuid.UUID] = None
    oggetti: List["Oggetto"] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def aggiungi_oggetto(self, oggetto: "Oggetto") -> None:
        """Aggiunge un oggetto all'inventario.

        Args:
            oggetto (Oggetto): Oggetto da aggiungere all'inventario.
        """
        self._aggiungi(oggetto)
        logger.info(f"[{self.id_proprietario}] Aggiunto oggetto '{oggetto.nome}' all'inventario.")

    def _aggiungi(self, oggetto: "Oggetto") -> None:
        """Aggiunge un oggetto all'inventario senza loggare.

        Args:
            oggetto (Oggetto): _Oggetto da aggiungere all'inventario.
        """
        self.oggetti.append(oggetto)

    def cerca_oggetto_per_id(self, oggetto_id: Union[str, uuid.UUID]) -> Optional["Oggetto"]:
        """ Cerca un oggetto nell'inventario per ID.

        Returns:
            Oggetto: L'oggetto trovato, o None se non esiste.
        """
        oggetto_id = str(oggetto_id)
        for obj in self.oggetti:
            if str(obj.id) == oggetto_id:
                return obj
        return None

    def cerca_oggetto_per_nome(self, nome: str) -> Optional["Oggetto"]:
        """Cerca un oggetto nell'inventario per nome.

        Returns:
            Oggetto: L'oggetto trovato, o None se non esiste.
        """
        for obj in self.oggetti:
            if obj.nome.lower() == nome.lower():
                return obj
        return None

    def mostra_inventario(self) -> None:
        """Mostra gli oggetti presenti nell'inventario."""

        if not self.oggetti:
            msg = "L'inventario è vuoto."
        else:
            msg = "Inventario:\n" + "\n".join(f"- {oggetto.nome}" for oggetto in self.oggetti)
        logger.info(f"[{self.id_proprietario}] {msg}")

    def mostra_lista_inventario(self) -> List["Oggetto"]:
        """ Restituisce una lista degli oggetti nell'inventario.

        Returns:
            List[Oggetto]: Lista degli oggetti presenti nell'inventario.
        """
        return self.oggetti.copy()

    def usa_oggetto(
        self,
        oggetto: "Oggetto",
        ambiente: Optional["Ambiente"] = None
    ) -> Optional[int]:
        """ Usa un oggetto dall'inventario, rimuovendolo se necessario.

        Args:
            oggetto (Oggetto): Oggetto da usare.
            ambiente (Optional[Ambiente]): Ambiente in cui l'oggetto viene usato oppure None
            se l'ambiente non è specificato.

        Returns:
            Optional[int]: Il valore dell'oggetto usato, o None se l'oggetto non è nell'inventario.
        """
        if not self.cerca_oggetto_per_id(oggetto.id):
            logger.info("Oggetto non trovato nell'inventario.")
            return None

        mod_ambiente = (
            ambiente.modifica_effetto_oggetto(
                oggetto.__class__.__name__,
                oggetto.valore
            ) if ambiente else 0
        )

        result = oggetto.usa(mod_ambiente=mod_ambiente)

        self.oggetti = [obj for obj in self.oggetti if obj.id != oggetto.id]
        logger.info(
            f"[{self.id_proprietario}] Usato e rimosso "
            f"oggetto '{oggetto.nome}'."
        )
        return result

    def rimuovi_oggetto(
        self,
        oggetto_id: Union[str, uuid.UUID]
    ) -> Optional[Oggetto]:
        """
        Rimuove un oggetto dall'inventario dato il suo ID.

        Args:
            oggetto_id (str | UUID): L'ID dell'oggetto da rimuovere.

        Returns:
            Oggetto: L'oggetto rimosso se trovato.
            None: Se nessun oggetto con quell'ID è stato trovato.
        """
        # Normalizziamo a stringa per confronto sicuro
        oggetto_id = str(oggetto_id)
        for oggetto in self.oggetti:
            if str(oggetto.id) == oggetto_id:
                self.oggetti.remove(oggetto)
                logger.info(
                    f"Oggetto '{oggetto.nome}' rimosso dall'inventario."
                )
                return oggetto
        logger.warning(
            f"Nessun oggetto con ID {oggetto_id} trovato nell'inventario."
        )
        return None
