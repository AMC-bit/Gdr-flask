
from dataclasses import dataclass, field
from typing import Optional
import random, uuid, json, os, logging
from gioco.personaggio import Personaggio
from gioco.classi import PersonaggioSchema
from gioco.ambiente import Ambiente, AmbienteFactory, AmbienteSchema
from gioco.oggetto import Oggetto, OggettoSchema
from gioco.inventario import Inventario
from gioco.schemas.personaggio import PersonaggioSchema
from gioco.schemas.missione_schema import MissioniSchema
from gioco.strategy import Strategia, StrategiaFactory, StrategiaSchema


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class Missione():
    """
    Si occupa di aggregare istanze di ambiente , nemici e ricompense
    Rappresenta una missione, composta da un ambiente, nemici e premi.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ambiente: Ambiente = field(default_factory=lambda: AmbienteFactory.usa_ambiente("Palude"))
    nemici: list[Personaggio] = field(default_factory=list)
    premi: list[Oggetto] = field(default_factory=list)
    nome: str = ""
    strategia_nemici: Optional[Strategia] = None
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
        if len(self.nemici) == 0:
            self.completata = True
            msg = f"Missione '{self.nome}' completata"
            logger.info(msg)
            return True
        return False

    # aggiunge premio all'inventario del giocatore se la missione è completata
    def assegna_premio(self, inventari_giocatori: list[Inventario], giocatore: str) -> None:
        """
        Mette nell'inventario dei giocatori gli oggetti contenuti nella lista
        dei Premi (Proprietà di Missione) distribuendoli casualmente

        Args:
            inventari_giocatori (list[Inventario]): Inventari a cui assegnare
            il premio

        Returns:
            None

        """
        for premio in self.premi:
            inventario = random.choice(inventari_giocatori)
            if inventario.id_proprietario is None:
                msg = "Non è possibile assegnare un premio ad un inventario"
                msg += "senza un personaggio"
                logger.warning(msg)
                raise ValueError(msg)
            inventario._aggiungi(premio)
            msg = f"Premio {premio.nome} aggiunto all'inventario di {giocatore} "
            logger.info(msg)

    # QUESTO METODO E' PROVVISORIO
    def check_missione(self, inventari_vincitori: list[Inventario]) -> None:
        """
        Questo metodo mette insieme gli altri nella giusta sequenza:
        Idealmente andrebbe chiamato dopo ogni attacco del giocatore
        Rimuovi i nemici sconfitti.
        Verifica completamento (dovrebbe funzionare anche con la lista dei
        nemici vuota) assegna il premio al giocatore_vincitore se la missione
        è completata

        Args:
            giocatore_vincitore (Personaggio): Usato per assegnargli il premio

        Returns:
            None
        """
        self.rimuovi_nemici_sconfitti()
        if self.verifica_completamento():
            self.assegna_premio(inventari_vincitori)

    # def to_dict(self) -> dict:
    #     """
    #     Restituisce uno stato serializzabile per session o JSON.

    #     Returns:
    #         dict: Dizionario del materiale serializzato
    #     """
    #     return {
    #         "id": str(self.id) if self.id else None,
    #         "classe": self.__class__.__name__,
    #         "nome": self.nome,
    #         "ambiente": Ambiente.to_dict(self.ambiente),
    #         "nemici": [Personaggio.to_dict(nemico) for nemico in self.nemici],
    #         "premi": [Oggetto.to_dict(premio) for premio in self.premi],
    #         "strategia_nemici": (
    #             Strategia.to_dict(self.strategia_nemici)
    #             if self.strategia_nemici else None
    #         ),
    #         "completata": self.completata,
    #         "attiva": self.attiva
    #     }

    # @classmethod
    # def from_dict(cls, data: dict) -> "Missione":
        """Ricostruisce l’istanza a partire da un dict serializzato.

        Args:
            data (dict): Dati serializzati

        Returns:
            Ambiente: Dati deserializzati
        """
        classi = {clss.__name__: clss for clss in Personaggio.__subclasses__()}

        ambiente_cls = Ambiente.from_dict(data["ambiente"])
        nemici = []
        for nemico in data.get("nemici", []):
            clss = classi.get(nemico.get("classe"))
            if clss:
                nemico = clss.from_dict(nemico)

                nemici.append(nemico)
        premi = [Oggetto.from_dict(premio) for premio in data.get("premi", [])]
        strategia_nemici = (
            Strategia.from_dict(data["strategia_nemici"])
            if data.get("strategia_nemici") else None
        )
        missione = cls(
            id=uuid.UUID(data["id"]) if data.get("id") else uuid.uuid4(),
            nome=data["nome"],
            ambiente=ambiente_cls,
            nemici=nemici,
            strategia_nemici=strategia_nemici,
            premi=premi
        )
        missione.completata = data.get("completata", False)
        missione.attiva = data.get("attiva", False)
        return missione


# Lista delle missioni

class GestoreMissioni():
    """
    È un gestore di istanze della classe Missione, e le gestisce con diversi
    metodi
    """

    def __init__(self) -> None:
        # La proprietà principale di GestoreMissioni sarà una lista
        # di oggetti Missione
        self.lista_missioni = self.setup()

    def setup(self) -> list[Missione]:
        """
        Istanzio le Missioni da fornire al GestoreMissioni,
        viene chiamato nel costruttore di GestoreMissioni
        cerca dentro alla cartella static le missioni
        e le istanzia in una lista di oggetti Missione
        Args:
            None

        Returns:
            list[Missione]: Ritorna una lista di istanze di classe Missione
        """

        # Istanzio le missioni
        # cerco dentro a static/mission ogni file json avrà lo stesso nome della missione,
        # il nome della sottoclasse di ambiente, il nome della sottoclasse della strategia
        # e la lista dei nemici e dei premi
        lista =[]
        routes = "static\mission\Imboscata"
        for files in os.listdir(routes):
            if files.endswith(".json"):
                with open(os.path.join(routes, files), 'r') as file:
                    data = json.load(file)
                    missione = Missione()
                    missione.nome = data["nome"]
                    missione.ambiente = AmbienteFactory.usa_ambiente(data["ambiente"])
                    missione.nemici =[]
                    for nemico in data["nemici"]:
                        # Uso PersonaggioSchema per caricare i nemici
                        # e creare le istanze corrette
                        if "classe" in nemico:
                            nemico = PersonaggioSchema().load(nemico)
                            missione.nemici.append(nemico)
                    missione.premi = [PozioneCura(), PozioneCura(), Medaglione()]
                    lista.append(missione)
        return lista

        # salva_principessa = Missione(
        #     nome="Salva la principessa",
        #     ambiente=Palude(),
        #     nemici=[Ladro("Megera furfante")],
        #     premi=[Medaglione()],

        #     strategia_nemici= StrategiaFactory.usa_strategia("difensiva")
        # )
        # print (f"{salva_principessa.to_dict}")

        # culto = Missione(
        #     nome="Sgomina il culto di Graz'zt sul vulcano Gheemir",
        #     ambiente=Vulcano(),
        #     nemici=[
        #         Mago("Cultista 1"),
        #         Mago("Cultista 2"),
        #         Mago("Cultista 3")
        #     ],
        #     premi=[PozioneCura(), Medaglione()],
        #     strategia_nemici= StrategiaFactory.usa_strategia("aggressiva")
        # )

        # return [imboscata, salva_principessa, culto]

    def mostra(self) -> None:
        """
        Mostra le missioni disponibili

        Args:
            None

        Returns:
            None
        """
        msg = ("Missioni disponibili:")
        logger.info(msg)
        for missione in self.lista_missioni:
            msg = f"-{missione.nome}"
            logger.info(msg)

    def finita(self) -> bool:
        """
        Controlla se in Missioni ci sono ancora missioni non completate in
        tal caso ritorna False, se tutte le missioni sono state completate
        ritorna True

        Args:
            None

        Returns:
            bool: Ritorna True se tutte le missioni sono state completate,
            altrimenti False
        """
        esito = True
        for missione in self.lista_missioni:
            if not missione.completata:
                esito = False
            if esito:
                missione.attiva = False
                msg = f"Missione : {missione.nome} completata"
                logger.info(msg)
        return esito

    def sorteggia(self) -> Missione | None:
        """
        Sorteggia una missione a caso tra quelle non completate in missioni e
        la ritorna , se non ci sono missioni non copletate ritorna False.

        Args:
            None

        Returns:
            Missione | None: Ritorna un'istanza di Missione non completata
            o None se il GestoreMissioni ha solo missioni completate
        """
        for missione in self.lista_missioni:
            if missione.attiva:
                return missione
        try:
            random.shuffle(self.lista_missioni)
            for missione in self.lista_missioni:
                if not missione.completata:
                    missione.attiva = True
                    return missione
            # Se non ci sono missioni che non siano state completate
            msg = "Non ci sono missioni non completate"
            raise ValueError(msg)
        except ValueError as e:
            msg = f"Errore: {e}"
            logger(msg)
            # Log.scrivi_log(msg)
            return None

