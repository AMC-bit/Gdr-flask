from .oggetto import Oggetto
from .personaggio import Personaggio
from .ambiente import Ambiente
# from utils.log import Log
# from utils.salvataggio import SerializableMixin, Json
# @SerializableMixin.register_class

class Inventario():
    """
    Gestisce la lista di oggetti posseduto da ogni personaggio
    Sarà la classe inventario a gestire le istanze di classe Oggetto
    """
    def __init__(self, proprietario : Personaggio = None )->None:
        self.oggetti = []
        self.proprietario = proprietario

    def aggiungi_oggetto(self, oggetto: Oggetto)->str:
        """
        Aggiungi un oggetto all'inventario.

        Args:
            oggetto (Oggetto): L'oggetto da aggiungere all'inventario.

        Return:
            str: risultato dell'aggiunta dell'oggetto all'inventario

        """
        self.oggetti.append(oggetto)
        msg = f"Aggiunto l'oggetto '{oggetto.nome}' all inventario. "
        return msg

    def _aggiungi(self, oggetto: Oggetto)-> None:
        """
        Aggiunge un oggetto all'inventario.

        Args:
            oggetto (Oggetto): L'oggetto da aggiungere all'inventario.

        Return:
            None
        """
        self.oggetti.append(oggetto)

    def cerca_oggetto(self, oggetto: Oggetto)-> bool | str:
        """
        cerca un oggetto specifico nell'inventario
        ritorna true se è presente o false se non c'è

        Args:
            oggetto (Oggetto): l'elemento da cercare all'interno della lista interna oggetti

        Returns:
            found (bool): risultato previsto della funzione per cercare un oggetto specifico
                ritorna true se viene trovato
                ritorna false se non è presente

            msg (str): Messaggio di errore.
        """
        msg =""
        try:
            found = False
            for obj in self.oggetti:
                if obj is oggetto:
                    found = True
                    break
            return found
        except Exception as e:
            msg = f"Errore generico: {e}"
            return msg

    def mostra_inventario(self)->str:
        """
        invia una stringa con la lista dei nomi degli oggetti presenti

        Args:
            None

        Return:
            msg (str): Messaggio che indica il contenuto dell'inventario.

        """
        msg = ""
        if len(self.oggetti) == 0:
            msg = "L'inventario è vuoto."
        else:
            msg = "Inventario :\n"
            for oggetto in self.oggetti :
                msg +=f"-{oggetto.nome}\n"
        return msg

    def mostra_lista_inventario(self)-> list[Oggetto] | str:
        """
        metodo che ritorna la lista degli oggetti presenti nell'inventario o una stringa per avvisare che l'inventario è vuoto:

        Args:
            None

        Return:
            list[Oggetto]: lista degli oggetti nell'inventario
            msg (str): Messaggio per avvisare che l'inventario è vuoto.

        """
        if len(self.oggetti) == 0:
            return "L'inventario è vuoto."
        else:
            return self.oggetti

    def usa_oggetto(
        self,
        oggetto : Oggetto,
        utilizzatore: Personaggio = None,
        bersaglio: Personaggio = None,
        ambiente: Ambiente = None)->str:
        """
        Utilizza un oggetto presente nell'inventario.

        Args:
            oggetto (Oggetto): oggetto da usare.
            utilizzatore (Personaggio): Il Personaggio che usa l'oggetto se non passato
            si proverà ad utilizzare quello presente in self.Proprietario se presente.
            bersaglio(Any): None di Default è un parametro opzionale che
            permette di usare un oggetto su un altro Personaggio che non sia l'utilizzatore.
            ambiente (Ambiente): L'ambiente può alterare il funzionamento degli
            oggetti

        Return:
            ritorno (str): ritorna una stringa con un messaggio dell'effettivo uso o un messaggio di errore

        """
        msg = ""
        if not utilizzatore and self.proprietario:
            utilizzatore=self.proprietario
        elif not utilizzatore and not self.proprietario:
            msg = "manca l'utilizzatore"
        elif self.cerca_oggetto(oggetto):
            msg = "l'oggetto non è stato trovato nell'inventario"
        else:
            if not bersaglio:
                bersaglio = utilizzatore
            if ambiente is None:
                mod_ambiente = 0
            else:
                mod_ambiente, msg = ambiente.modifica_effetto_oggetto(oggetto)
                msg += "\n"
            msg += oggetto.usa(
                utilizzatore,
                bersaglio,
                mod_ambiente=mod_ambiente
            )
            self.oggetti.remove(oggetto)
        #
        # dati_salvataggio = [self.to_dict(), bersaglio.to_dict()]
        # for dati in dati_salvataggio:
        #     Json.scrivi_dati("data/salvataggio.json", Json.applica_patch(dati))
        return msg

    def riversa_inventario(self, da_inventario : 'Inventario')-> str:
        """
        Permette ad un inventario di prendere tutti gli oggetti di un altro inventario(da_inventario)

        Args:
            da_inventario(Inventario): L'inventario da cui vengono prelevati tutti gli oggetti.

        Return:
            risultato (str): Messaggio che indica gli oggetti trasferiti o che l'inventario è vuoto.

        """
        msg = ""
        if len(da_inventario.oggetti) != 0 :
            if self.proprietario == None:
                msg = "Inseriti nell'inventario : "
                # Log.scrivi_log("Oggetti trasferiti da un inventario a un altro. ")
            else:
                msg = f"{self.proprietario.nome} raccoglie :"
                # Log.scrivi_log(f"{self.proprietario.nome} ha raccolto oggetti dall'inventario di un altro personaggio. ")
            for oggetto in da_inventario.oggetti :
                msg= f"\n - {oggetto.nome}"
                # Log.scrivi_log(f"{oggetto.nome} trasferito nell'inventario. ")
                self._aggiungi(oggetto)
            da_inventario.oggetti.clear()
        else:
            if da_inventario.proprietario == None:
                msg = "l'inventario è vuoto."
            else:
                msg = f"L'inventario di {da_inventario.proprietario.nome} è vuoto"
            # Log.scrivi_log(msg)
        return msg

