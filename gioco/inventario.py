import uuid
import logging
from gioco.oggetto import Oggetto
from gioco.ambiente import Ambiente
from typing import List, Optional, Union
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class Inventario:
    """
    Gestisce la lista di oggetti posseduto da ogni personaggio
    Sarà la classe inventario a gestire le istanze di classe Oggetto
    """
    id_proprietario: Optional[uuid.UUID] = None
    oggetti: List[Oggetto] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def aggiungi_oggetto(self, oggetto: Oggetto)->None:
        """
        Aggiungi un oggetto all'inventario.
        la stringa di testo viene aggiunta alla stringa di messaggi

        Args:
            oggetto (Oggetto): L'oggetto da aggiungere all'inventario.

        Return:
            None

        """
        self._aggiungi(oggetto)
        logger.info(f"Aggiunto l'oggetto '{oggetto.nome}' all inventario. ")

    def _aggiungi(self, oggetto: Oggetto)-> None:
        """
        Aggiunge un oggetto all'inventario il metodo al momento è previsto come
        interno alla classe, ma può essere usato anche fuori.
        Serve sia allo scopo di  aggiungere un oggetto all'inventario senza
        un messaggio di ritorno (opzionale) sia per non mostrare direttamente
        con un append la lista oggetti qualora servisse anche esternamente.

        Args:
            oggetto (Oggetto): L'oggetto da aggiungere all'inventario.

        Return:
            None
        """
        self.oggetti.append(oggetto)

    def cerca_oggetto(self, oggetto: Oggetto) -> Union[bool, None]:
        """
        cerca un oggetto specifico nell'inventario
        ritorna true se è presente o false se non c'è
        se avviene un errore ritorna None e aggiunge un messaggio di errore
        alla stringa di messaggi.

        Args:
            oggetto (Oggetto): l'elemento da cercare all'interno della lista interna oggetti

        Returns:
            found (bool): risultato previsto della funzione per cercare un oggetto specifico
                ritorna true se viene trovato
                ritorna false se non è presente

            None.
        """
        try:
            found = False
            for obj in self.oggetti:
                if obj is oggetto:
                    found = True
                    break
            return found
        except Exception as e:
            logger.error(f"Errore durante la ricerca dell'oggetto: {e}")
            return None

    def mostra_inventario(self)->None:
        """
        invia una stringa con la lista dei nomi degli oggetti presenti
        alla classe Messaggi.

        Args:
            None

        Return:
            None.

        """
        if len(self.oggetti) == 0:
            msg = "L'inventario è vuoto."
        else:
            msg = "Inventario :\n"
            for oggetto in self.oggetti :
                msg +=f"-{oggetto.nome}\n"
        logger.info(msg)

    def mostra_lista_inventario(self)-> Union[list[Oggetto], str, None]:
        """
        metodo che ritorna la lista degli oggetti presenti nell'inventario
        o invia una stringa a Messaggi per avvisare che l'inventario è vuoto:

        Args:
            None

        Return:
            list[Oggetto]: lista degli oggetti nell'inventario
            str: messaggio di inventario vuoto
            None: solo se si verificano problemi
        """
        if len(self.oggetti) == 0:
            msg = "L'inventario è vuoto."
            logger.info(msg)
            return msg
        else:
            return self.oggetti

    def usa_oggetto(
        self,
        oggetto : Oggetto,
        ambiente: Ambiente = None)-> int|None:
        """
        Utilizza un oggetto presente nell'inventario.

        Args:
            oggetto (Oggetto): oggetto da usare.
            ambiente (Ambiente): L'ambiente può alterare il funzionamento degli
            oggetti

        Return:
            int: il risultato dell'uso dell'oggetto, se l'oggetto è stato
            trovato e usato correttamente.
            None: se l'oggetto non è stato trovato nell'inventario.
        """
        result = None
        if not self.cerca_oggetto(oggetto):
            msg = "l'oggetto non è stato trovato nell'inventario"
            logger.info(msg)
        else:
            mod_ambiente = (
                ambiente.modifica_effetto_oggetto(oggetto)
                if ambiente else 0
            )
            result = oggetto.usa(
                mod_ambiente=mod_ambiente
            )
            self.oggetti.remove(oggetto)
        return result

    def rimuovi_oggetto(self, oggetto_id: Union[str, uuid.UUID]) -> Optional[Oggetto]:
        """
        Rimuove un oggetto dall'inventario dato il suo ID.

        Args:
            oggetto_id (str | UUID): L'ID dell'oggetto da rimuovere.

        Returns:
            Oggetto: L'oggetto rimosso se trovato.
            None: Se nessun oggetto con quell'ID è stato trovato.
        """
        oggetto_id = str(oggetto_id)  # Normalizziamo a stringa per confronto sicuro
        for oggetto in self.oggetti:
            if str(oggetto.id) == oggetto_id:
                self.oggetti.remove(oggetto)
                logger.info(f"Oggetto '{oggetto.nome}' rimosso dall'inventario.")
                return oggetto
        logger.warning(f"Nessun oggetto con ID {oggetto_id} trovato nell'inventario.")
        return None
