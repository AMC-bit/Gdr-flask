from dataclasses import dataclass, field
import uuid
from enum import Enum
from gioco.log import get_logger

'''
1 - TipoOggetto come Enum Se scrivi "Buff" invece di "buff", o "Ristorativo" invece di "Ristoravito"
il codice con le stringhe non se ne accorge solo a runtime, invce cosi avvisa subito
si puo cambiare il nome di un tipo (“Offensivo” “Attacco”), lo fai UNA volta nell’Enum e in tutto il codice cambi solo quell’istanza
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
    RISTORATIVO = "Ristorativo"
    OFFENSIVO = "Offensivo"
    BUFF = "Buff"

@dataclass
class Oggetto:
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
        """Metodo astratto da sovrascrivere nelle sottoclassi."""
        logger.info(f"{self.nome}: uso non implementato.")
        raise NotImplementedError("Questo oggetto non ha effetto definito.")

# OGGETTI

@dataclass
class PozioneCura(Oggetto):
    nome: str = "Pozione Rossa"
    valore: int = 30
    tipo_oggetto: TipoOggetto = TipoOggetto.RISTORATIVO

    def usa(self, mod_ambiente: int = 0) -> int:
        self.usato = True
        cura = self.valore + mod_ambiente
        logger.info(f"{self.nome} usata: cura {cura} HP.")
        return cura

@dataclass
class BombaAcida(Oggetto):
    nome: str = "Bomba Acida"
    valore: int = 30
    tipo_oggetto: TipoOggetto = TipoOggetto.OFFENSIVO

    def usa(self, mod_ambiente: int = 0) -> int:
        self.usato = True
        danno = - (self.valore + mod_ambiente)
        logger.info(f"{self.nome} lanciata: infligge {abs(danno)} danni.")
        return danno

@dataclass
class Medaglione(Oggetto):
    nome: str = "Medaglione"
    valore: int = 10
    tipo_oggetto: TipoOggetto = TipoOggetto.BUFF

    def usa(self, mod_ambiente: int = 0) -> int:
        self.usato = True
        mod = self.valore + mod_ambiente
        logger.info(f"{self.nome} attivato: bonus {mod} all'attacco_max.")
        return mod

@dataclass
class PozioneSuperCura(PozioneCura):
    nome: str = "Super Pozione Rossa"
    valore: int = 100

    def usa(self, mod_ambiente: int = 0) -> int:
        # Log base (PozioneCura)
        cura = super().usa(mod_ambiente)
        # Logica/Logging extra
        logger.info(f"{self.nome}: È una super pozione! Effetto potenziato.")
        return cura