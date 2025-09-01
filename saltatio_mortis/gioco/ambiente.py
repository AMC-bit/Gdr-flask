import random
from typing import Dict
from dataclasses import dataclass
from utils.log import get_logger

'''
1- Logger
2- Factory accetta sia numeri che stringhe tipo dizionario in modo da
    selezionare come numero in console
3- Unificati mod_ modifica_
'''

logger = get_logger(__name__)


@dataclass
class Ambiente:
    """
    Gestisce i modificatori ambientali per Personaggio e Oggetto.

    Attributi:
        nome (str): Nome dell'ambiente.
        mod_attacco (int): Modificatore di attacco per i personaggi.
        mod_cura (int): Modificatore di cura per i personaggi.

    Metodi:
        modifica_attacco:
            Modifica l'attacco del personaggio in base alla compatibilità
            della classe del personaggio con l'ambiente.
        modifica_effetto_oggetto:
            Modifica l'effetto di un oggetto in base alla compatibilità
            dell'oggetto con l'ambiente.
        modifica_cura:
            Modifica le capacità di cura del personaggio alla fine di
            una missione in base alla compatibilità della classe del
            personaggio con l'ambiente.
    """
    nome: str
    mod_attacco: int = 0
    mod_cura: int = 0

    def modifica_attacco(
        self,
        classe_attaccante: str,
        nome_attaccante: str
    ) -> int:
        """
        Modifica l'attacco del personaggio in base alla sinergia
        tra la classe del personaggio e l'ambiente.
        Questo metodo deve essere implementato nelle sottoclassi.

        Args:
            classe_attaccante (str): Classe del personaggio che attacca.
            nome_attaccante (str): Nome del personaggio che attacca.

        Raises:
            NotImplementedError:
                Se il metodo non è implementato nelle sottoclassi.

        Returns:
            int: Il modificatore di attacco da applicare al personaggio.
        """
        raise NotImplementedError

    def modifica_effetto_oggetto(
        self,
        classe_oggetto: str,
        valore_oggetto: int
    ) -> int:
        """
        Modifica l'effetto di un oggetto in base alla sua sinergia con
        l'ambiente circostante.
        Questo metodo deve essere implementato nelle sottoclassi.

        Args:
            classe_oggetto (str): Classe dell'oggetto.
            valore_oggetto (int): Valore dell'effetto dell'oggetto.

        Raises:
            NotImplementedError:
                Se il metodo non è implementato nelle sottoclassi.

        Returns:
            int: Il modificatore di effetto da applicare all'oggetto.
        """
        raise NotImplementedError

    def modifica_cura(self, classe_soggetto: str, nome_soggetto: str) -> int:
        """
        Modifica la cura del personaggio alla fine di una missione in base
        alla capacità della classe del personaggio di
        curarsi in un ambiente specifico.

        Args:
            classe_soggetto (str): Classe del soggetto che si cura.
            nome_soggetto (str): Nome del soggetto che si cura.

        Raises:
            NotImplementedError: Se il metodo non è implementato nelle sottoclassi.

        Returns:
            int: Il modificatore di cura da applicare alla cura del soggetto.
        """
        raise NotImplementedError



@dataclass
class Foresta(Ambiente):
    """
    Rappresenta un ambiente di foresta con modificatori specifici
    per attacco e cura.
    Attributi:
        nome (str): Nome dell'ambiente, in questo caso "Foresta".
        mod_attacco (int): Modificatore di attacco per i personaggi
            che attaccano in questo ambiente.
        mod_cura (int): Modificatore di cura per i personaggi
            che si curano in questo ambiente.
    """
    nome: str = "Foresta"
    mod_attacco: int = 5
    mod_cura: int = 5

    def modifica_attacco(
        self,
        classe_attaccante: str,
        nome_attaccante: str
    ) -> int:
        """
        Modifica l'attacco del personaggio in base alla compatibilità
        della classe del personaggio con l'ambiente Foresta.
        In questo caso, se il personaggio è un Guerriero,
        guadagna un bonus di attacco.

        Args:
            classe_attaccante (str): Classe del personaggio che attacca.
            nome_attaccante (str): Nome del personaggio che attacca.

        Returns:
            int: Il modificatore di attacco da applicare al personaggio.
        """
        if classe_attaccante == "Guerriero":
            logger.info(
                f"{nome_attaccante} guadagna {self.mod_attacco} "
                f"attacco nella Foresta!"
            )
            return self.mod_attacco
        return 0

    def modifica_effetto_oggetto(
        self,
        classe_oggetto: str,
        valore_oggetto: int
    ) -> int:
        """
        Modifica l'effetto di un oggetto in base alla sua sinergia con
        l'ambiente circostante.
        In questo caso, la foresta non modifica l'effetto degli oggetti.

        Args:
            classe_oggetto (str): Classe dell'oggetto.
            valore_oggetto (int): Valore dell'effetto dell'oggetto.

        Returns:
            int: Il modificatore di effetto da applicare all'oggetto.
        """
        return 0

    def modifica_cura(self, classe_soggetto: str, nome_soggetto: str) -> int:
        """
        Modifica la cura del personaggio alla fine di una missione in base
        alla capacità della classe del personaggio di curarsi in un ambiente.
        In questo caso, se il personaggio è un Ladro,
        guadagna un bonus di cura, altrimenti non ci sono bonus o malus.

        Args:
            classe_soggetto (str): Classe del soggetto che si cura.
            nome_soggetto (str): Nome del soggetto che si cura.

        Returns:
            int: Il modificatore di cura da applicare alla cura del soggetto.
        """
        if classe_soggetto == "Ladro":
            logger.info(
                f"{nome_soggetto} guadagna {int(self.mod_cura)} cura "
                f"extra in Foresta!"
            )
            return int(self.mod_cura)
        return 0


@dataclass
class Vulcano(Ambiente):
    """
    Rappresenta un ambiente di vulcano con modificatori specifici
    per attacco e cura.

    Attributi:
        nome (str): Nome dell'ambiente, in questo caso "Vulcano".
        mod_attacco (int): Modificatore di attacco per i personaggi
            che attaccano in questo ambiente.
        mod_cura (int): Modificatore di cura per i personaggi
            che si curano in questo ambiente.
    """
    nome: str = "Vulcano"
    mod_attacco: int = 10
    mod_cura: int = -5

    def modifica_attacco(
        self,
        classe_attaccante: str,
        nome_attaccante: str
    ) -> int:
        """
        Modifica l'attacco del personaggio in base alla compatibilità
        della classe del personaggio con l'ambiente Vulcano.
        In questo caso, se il personaggio è un Mago,
        guadagna un bonus di attacco, mentre se è un Ladro,
        subisce un malus di attacco.

        Args:
            classe_attaccante (str): Classe del personaggio che attacca.
            nome_attaccante (str): Nome del personaggio che attacca.

        Returns:
            int: Modificatore di attacco da applicare al personaggio.
        """

        if classe_attaccante == "Mago":
            logger.info(
                f"{nome_attaccante} guadagna {self.mod_attacco} "
                f"attacco nel Vulcano!"
            )
            return self.mod_attacco
        elif classe_attaccante == "Ladro":
            logger.info(
                f"{nome_attaccante} perde {self.mod_attacco} attacco "
                f"nel Vulcano!"
            )
            return -self.mod_attacco
        return 0

    def modifica_effetto_oggetto(
        self,
        classe_oggetto: str,
        valore_oggetto: int
    ) -> int:
        """
        Modifica l'effetto di un oggetto in base alla sua sinergia con
        l'ambiente circostante.
        In questo caso, se l'oggetto è una Bomba Acida,
        guadagna un bonus di danni casuali tra 0 e 15, in caso contrario
        non ci sono modifiche.

        Args:
            classe_oggetto (str): Classe dell'oggetto.
            valore_oggetto (int): Valore dell'effetto dell'oggetto.

        Returns:
            int: Il modificatore di effetto da applicare all'oggetto.
        """

        if classe_oggetto == "BombaAcida":
            variazione = random.randint(0, 15)
            logger.info(
                f"Nella {self.nome}, la Bomba Acida guadagna "
                f"{variazione} danni!"
            )
            return variazione
        return 0

    def modifica_cura(self, classe_soggetto: str, nome_soggetto: str) -> int:
        """
        Modifica la cura del personaggio alla fine di una missione in base
        alla capacità della classe del personaggio di curarsi in un ambiente.
        In questo caso, tutti i personaggi subiscono un malus di cura
        di 5 punti.

        Args:
            classe_soggetto (str): Classe del soggetto che si cura.
            nome_soggetto (str): Nome del soggetto che si cura.

        Returns:
            int: Il modificatore di cura da applicare alla cura del soggetto.
        """
        logger.info(
            f"{nome_soggetto} subisce malus di cura {self.mod_cura} "
            f"in Vulcano!"
        )
        return self.mod_cura


@dataclass
class Palude(Ambiente):
    """
    Rappresenta un ambiente di palude con modificatori specifici
    per attacco e cura.
    Attributi:
        nome (str): Nome dell'ambiente, in questo caso "Palude".
        mod_attacco (int): Modificatore di attacco per i personaggi
            che attaccano in questo ambiente.
        mod_cura (float): Modificatore di cura per i personaggi
            che si curano in questo ambiente.
    Metodi:
        modifica_attacco: Modifica l'attacco del personaggio in base
            all'ambiente.
        modifica_effetto_oggetto: Modifica l'effetto di un oggetto
            in base all'ambiente.
        modifica_cura: Modifica la cura del personaggio in base
            all'ambiente.
    """
    nome: str = "Palude"
    mod_attacco: int = -5
    mod_cura: int = 3

    def modifica_attacco(
        self,
        classe_attaccante: str,
        nome_attaccante: str
    ) -> int:
        """
        Modifica l'attacco del personaggio in base all'ambiente.
        In questo caso, i Guerrieri e i Ladri subiscono un malus di
        attacco di 5 punti.

        Args:
            classe_attaccante (str): Classe del personaggio che attacca.
            nome_attaccante (str): Nome del personaggio che attacca.

        Returns:
            int: Il modificatore di attacco da applicare al personaggio.
        """
        if classe_attaccante in ["Guerriero", "Ladro"]:
            logger.info(
                f"{nome_attaccante} perde {-self.mod_attacco} "
                f"attacco nella Palude!"
            )
            return self.mod_attacco
        return 0

    def modifica_effetto_oggetto(
        self,
        classe_oggetto: str,
        valore_oggetto: int
    ) -> int:
        """
        Modifica l'effetto di un oggetto in base all'ambiente.
        In questo caso, la Pozione Cura subisce una riduzione del
        suo effetto di cura del 30%.

        Args:
            classe_oggetto (str): Classe dell'oggetto.
            valore_oggetto (int): Valore dell'oggetto.

        Returns:
            int: Il modificatore di effetto da applicare all'oggetto.
        """
        if classe_oggetto == "PozioneCura":
            riduzione = int(valore_oggetto * self.mod_cura)
            logger.info(
                f"Nella {self.nome}, la Pozione Cura ha effetto "
                f"ridotto di {riduzione} punti!"
            )
            return -riduzione
        return 0

    def modifica_cura(self, classe_soggetto: str, nome_soggetto: str) -> int:
        """
        Modifica la cura del personaggio in base all'ambiente.
        In questo caso, i Maghi ricevono un bonus del 12% della loro salute
        rimanente alla loro capacità di cura.

        Args:
            classe_soggetto (str): Classe del personaggio che si cura.
            nome_soggetto (str): Nome del personaggio che si cura.

        Returns:
            int: Il modificatore di cura da applicare alla cura del personaggio.
        """
        if classe_soggetto == "Mago":
            cura_effettiva = self.mod_cura * 20
            logger.info(
                f"{nome_soggetto} incrementa la sua capacità di cura "
                f"del {(round(float(cura_effettiva/5.0), 2))}% "
                f"della sua salute rimanente in Palude!"
            )
            return cura_effettiva
        return 0


class AmbienteFactory:
    """
    Factory per la generazione di ambienti.
    """
    @staticmethod
    def get_opzioni() -> Dict[str, Ambiente]:
        """
        Metodo statico che restituisce un dizionario di opzioni
        degli ambienti disponibili.
        Le chiavi sono sia numeri che nomi degli ambienti,
        permettendo una selezione flessibile.
        Args:
            None.
        Returns:
            Dict[str, Ambiente]: Un dizionario con le opzioni di ambiente.
        """
        return {
            "1": Foresta(),
            "foresta": Foresta(),
            "2": Vulcano(),
            "vulcano": Vulcano(),
            "3": Palude(),
            "palude": Palude()
        }

    @staticmethod
    def usa_ambiente(scelta: str) -> Ambiente:
        """
        Metodo statico che restituisce un ambiente in base alla scelta
        dell'utente. Se la scelta non è valida, restituisce Foresta
        come opzione di default

        Args:
            scelta (str): La scelta dell'utente per l'ambiente.

        Returns:
            Ambiente: ambiente corrispondente alla scelta dell'utente,
                o Foresta se la scelta non è valida.
        """
        mapping = AmbienteFactory.get_opzioni()
        chiave = str(scelta).strip().lower()
        if chiave in mapping:
            env = mapping[chiave]
            logger.info(f"Selezionato ambiente: {env.nome}")
            return env
        logger.warning(
            f"Scelta ambiente sconosciuta: {scelta}, uso Foresta di default."
        )
        return Foresta()

    @staticmethod
    def ambiente_random() -> Ambiente:
        """
        Restituisce un ambiente casuale dalla lista degli ambienti disponibili.

        Returns:
            Ambiente: Un ambiente casuale.
        """
        opzioni = list(
            {
                k: v for k, v in AmbienteFactory.get_opzioni().items()
                if len(k) == 1
            }.values()
        )
        random_choice = random.choice(opzioni)
        logger.info(f"Ambiente Casuale Selezionato: {random_choice.nome}")
        return random_choice
