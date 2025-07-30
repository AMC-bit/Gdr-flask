from dataclasses import dataclass, field
import uuid
from enum import Enum
from utils.log import get_logger

'''
1 - TipoOggetto come Enum Se scrivi "Buff" invece di "buff", o "Ristorativo" invece di "Ristoravito"
il codice con le stringhe non se ne accorge solo a runtime, invce cosi avvisa subito
si puo cambiare il nome di un tipo (“Offensivo” “Attacco”), lo fai UNA volta
nell'Enum e in tutto il codice cambi solo quell'istanza
miglioramenti in logica
con stringa
if oggetto.tipo_oggetto == "Buff":  # funziona
if oggetto.tipo_oggetto == "buff":  # non funziona
con enum
oggetto = PozioneCura()
if oggetto.tipo_oggetto == TipoOggetto.RISTORATIVO:
    print("È una pozione!")

2- super() per loggare informazioni base, e aggiungere logica extra
'''

logger = get_logger(__name__)

# Enum per i tipi di oggetto
class TipoOggetto(Enum):
    """
    Rappresenta i diversi tipi di oggetti nel gioco.
    Ogni tipo ha un nome che può essere utilizzato per identificare
    il tipo di oggetto in modo più leggibile e sicuro rispetto all'uso
    di stringhe.

    Attributes:
        RISTORATIVO (str): Oggetto che ripristina salute o risorse.
        OFFENSIVO (str): Oggetto che infligge danni o effetti negativi.
        BUFF (str): Oggetto che fornisce bonus o miglioramenti temporanei.
    """
    RISTORATIVO = "Ristorativo"
    OFFENSIVO = "Offensivo"
    BUFF = "Buff"

@dataclass
class Oggetto:
    """
    Classe base per gli oggetti del gioco.
    Questa classe definisce le proprietà comuni per tutti gli oggetti,
    come nome, stato di utilizzo, valore e tipo di oggetto.
    Attributes:
        nome (str): Il nome dell'oggetto.
        usato (bool): Indica se l'oggetto è stato utilizzato.
        valore (int): Il valore dell'oggetto, che può influenzare gli effetti.
        tipo_oggetto (TipoOggetto): Il tipo di oggetto,
            definito dall'enum TipoOggetto.
        id (uuid.UUID): Un identificatore unico per l'oggetto.
        classe (str): Il nome della classe dell'oggetto,
            impostato automaticamente.
    Methods:
        usa(mod_ambiente: int = 0): Metodo astratto da sovrascrivere
            nelle sottoclassi.
    """

    nome: str
    usato: bool = False
    valore: int = 30
    tipo_oggetto: TipoOggetto = TipoOggetto.BUFF
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    classe: str = field(init=False)

    def __post_init__(self):
        # Imposta automaticamente il nome della classe
        self.classe = self.__class__.__name__

    def usa(self, mod_ambiente: int = 0):
        """
        Metodo astratto da sovrascrivere nelle sottoclassi per definire
        l'effetto dell'oggetto quando viene utilizzato.
        Se non implementato, solleva un'eccezione NotImplementedError.
        Args:
            mod_ambiente (int): Modificatore di ambiente che può influenzare
                l'effetto dell'oggetto.
        Raises:
            NotImplementedError: Se il metodo non è implementato nella
                sottoclasse.
        """
        logger.info(f"{self.nome}: uso non implementato.")
        raise NotImplementedError("Questo oggetto non ha effetto definito.")

# OGGETTI

@dataclass
class PozioneCura(Oggetto):
    """
    Classe per le pozioni curative.
    Questa classe rappresenta una pozione che può essere utilizzata
    per curare il personaggio, ripristinando una quantità fissa di salute.
    """
    nome: str = "Pozione Rossa"
    valore: int = 30
    tipo_oggetto: TipoOggetto = TipoOggetto.RISTORATIVO

    def usa(self, mod_ambiente: int = 0) -> int:
        """
        Usa la pozione per curare un personaggio.
        Al valore della pozione aggiunge il modificatore
        dell'ambiente all'effetto di cura.

        Args:
            mod_ambiente (int): Modificatore di ambiente che può influenzare
                l'effetto della cura. il valore di default è 0.

        Returns:
            tuple[int, TipoOggetto]:
                La quantità di salute curata e il tipo di oggetto
                (in questo caso RISTORATIVO).
        """
        self.usato = True
        cura = self.valore + mod_ambiente
        logger.info(f"{self.nome} usata: cura {cura} HP.")
        return cura, self.tipo_oggetto

@dataclass
class BombaAcida(Oggetto):
    """
    Classe per le bombe acide.
    Questa classe rappresenta un oggetto che infligge un danno specifico
    al nemico bersagliato.
    """
    nome: str = "Bomba Acida"
    valore: int = 30
    tipo_oggetto: TipoOggetto = TipoOggetto.OFFENSIVO

    def usa(self, mod_ambiente: int = 0) -> tuple[int, TipoOggetto]:
        """
        Usa la bomba acida per infliggere danni al nemico.
        Al valore della bomba aggiunge il modificatore di ambiente.

        Args:
            mod_ambiente (int, optional): Un modificatore di ambiente che può
            influenzare l'effetto della bomba.
            Se non passato il valore di default è 0.

        Returns:
            tuple[int, TipoOggetto]:
                La quantità di danno inflitto e il tipo di oggetto
                (in questo caso OFFENSIVO).
        """
        self.usato = True
        danno = - (self.valore + mod_ambiente)
        logger.info(f"{self.nome} lanciata: infligge {abs(danno)} danni.")
        return danno, self.tipo_oggetto

@dataclass
class Medaglione(Oggetto):
    """
    Classe per il medaglione.
    Questa classe rappresenta un oggetto che fornisce un bonus all'attacco
    dell'utilizzatore quando viene attivato.
    """
    nome: str = "Medaglione"
    valore: int = 10
    tipo_oggetto: TipoOggetto = TipoOggetto.BUFF

    def usa(self, mod_ambiente: int = 0) -> tuple[int, TipoOggetto]:
        """
        Usa il medaglione per fornire un bonus all'attacco.
        Al valore del medaglione aggiunge un possibile modificatore ambientale.

        Args:
            mod_ambiente (int, optional): Modificatore ambientale che può influenzare
                l'effetto del medaglione. Il valore di default è 0.

        Returns:
            tuple[int, TipoOggetto]:
                La quantità di bonus all'attacco e il tipo di oggetto
                (in questo caso BUFF).
        """
        self.usato = True
        mod = self.valore + mod_ambiente
        logger.info(f"{self.nome} attivato: bonus {mod} all'attacco_max.")
        return mod, self.tipo_oggetto

@dataclass
class PozioneSuperCura(PozioneCura):
    """
    Classe derivata da PozioneCura per le super pozioni curative.
    Questa classe rappresenta una pozione che può essere utilizzata
    per curare il personaggio, ripristinando una grande quantità di salute,
    potenzialmente curando l'intera salute del personaggio.
    """
    nome: str = "Super Pozione Rossa"
    valore: int = 100

    def usa(self, mod_ambiente: int = 0) -> tuple[int, TipoOggetto]:
        """
        Usa la super pozione per curare un personaggio.
        Al valore della super pozione aggiunge il modificatore ambientale.

        Args:
            mod_ambiente (int, optional): Modificatore ambientale che può influenzare
                l'effetto della super pozione. Di defaults è pari a 0.

        Returns:
            tuple[int, TipoOggetto]:
            La quantità di salute curata e il tipo di oggetto
                (in questo caso RISTORATIVO).
        """
        # Log base (PozioneCura)
        cura = super().usa(mod_ambiente)
        # Logica/Logging extra
        logger.info(f"{self.nome}: È una super pozione! Effetto potenziato.")
        return cura, self.tipo_oggetto