import random, logging
from gioco.ambiente import Ambiente
from gioco.inventario import Inventario
from enum import Enum

'''
1- dataclass per le strategie non serve, non ci sono campi dinamici da serializzare (basta l’attributo nome)
2- il logger è già configurato in gioco/__init__.py, non serve ripeterlo qui
3- Costruttori con super() per logging coerente e possibilità di parametri
4- Enum
'''

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TipoStrategia(Enum):
    AGGRESSIVA = "aggressiva"
    DIFENSIVA = "difensiva"
    EQUILIBRATA = "equilibrata"

class Strategia:
    nome = "Strategia base"

    def __init__(self):
        logger.info(f"[Strategia] Selezionata: {self.nome}")

    def uso_inventario_npc(
        self,
        salute_npc: int,
        inventario: Inventario,
        ambiente: Ambiente = None,
    ) -> int | None:
        logger.info(f"[Strategia {self.nome}] Nessun comportamento specificato.")
        raise NotImplementedError("Implementare nelle sottoclassi.")

    def bonus_destrezza(self, destrezza: int) -> int:
        return destrezza

    def malus_destrezza(self, destrezza: int) -> int:
        return destrezza

class Aggressiva(Strategia):
    nome = "Aggressiva"

    def __init__(self):
        super().__init__()
        logger.info("NPC userà strategia AGGRESSIVA: danni massimi!")

    def uso_inventario_npc(self, salute_npc, inventario, ambiente=None):
        if inventario and inventario.oggetti:
            ogg = next((o for o in inventario.oggetti if o.nome == "Bomba Acida"), None)
            if ogg and random.random() < 0.5:  # 50%
                logger.info("NPC usa Bomba Acida!")
                return inventario.usa_oggetto(oggetto=ogg, ambiente=ambiente)
        logger.info("NPC non usa oggetti (Aggressiva).")
        return None


class Difensiva(Strategia):
    nome = "Difensiva"

    def __init__(self):
        super().__init__()
        logger.info("NPC userà strategia DIFENSIVA: si cura se serve.")

    def uso_inventario_npc(self, salute_npc, inventario, ambiente=None):
        if salute_npc < 60 and inventario and inventario.oggetti:
            ogg = next((o for o in inventario.oggetti if o.nome == "Pozione Rossa"), None)
            if ogg and random.random() < 0.5:
                logger.info("NPC usa Pozione Rossa (Difensiva).")
                return inventario.usa_oggetto(oggetto=ogg, ambiente=ambiente)
        logger.info("NPC non usa oggetti (Difensiva).")
        return None


class Equilibrata(Strategia):
    nome = "Equilibrata"

    def __init__(self):
        super().__init__()
        logger.info("NPC userà strategia EQUILIBRATA.")

    def uso_inventario_npc(self, salute_npc, inventario, ambiente=None):
        if salute_npc < 40:
            ogg = next((o for o in inventario.oggetti if o.nome == "Pozione Rossa"), None)
            if ogg and random.random() < 0.33:
                logger.info("NPC usa Pozione Rossa (Equilibrata).")
                return inventario.usa_oggetto(oggetto=ogg, ambiente=ambiente)
        else:
            ogg = next((o for o in inventario.oggetti if o.nome == "Bomba Acida"), None)
            if ogg and random.random() < 0.33:
                logger.info("NPC usa Bomba Acida (Equilibrata).")
                return inventario.usa_oggetto(oggetto=ogg, ambiente=ambiente)
        logger.info("NPC non usa oggetti (Equilibrata).")
        return None

# --------- FACTORY ------------

class StrategiaFactory:
    _mappa = {
        TipoStrategia.AGGRESSIVA: Aggressiva,
        TipoStrategia.DIFENSIVA: Difensiva,
        TipoStrategia.EQUILIBRATA: Equilibrata
    }

    @staticmethod
    def strategia_random() -> Strategia:
        cls = random.choice(list(StrategiaFactory._mappa.values()))
        return cls()

    @staticmethod
    def usa_strategia(tipo: str) -> Strategia:
        try:
            tipo_enum = TipoStrategia(tipo.lower())
            return StrategiaFactory._mappa[tipo_enum]()
        except (ValueError, KeyError):
            raise ValueError(f"Tipo di strategia sconosciuto: {tipo}")



