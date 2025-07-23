import random, logging
from gioco.personaggio import Personaggio

from dataclasses import dataclass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@dataclass
class Mago(Personaggio):
    """
    Classe che rappresenta un personaggio mago.
    Estende la classe personaggio con attacco diminuito e recupero
    di salute personalizzato
    """
    salute_max: int = 80
    salute: int = salute_max
    attacco_min: int = 0
    attacco_max: int = 90
    iniziativa: int = 15


    def attacca(self, mod_ambiente: int = 0) -> tuple[int, str]:
        """
        Il Mago ha attacco minimo diminuito di 5 e attacco massimo
        aumentato di 10

        Args:
            bersaglio (Personaggio): personaggio che subisce l'attacco
            mod_ambiente (int): modificatore ambientale di attacco (default: 0)

        Returns:
            tuple[int, str]: danno inflitto all'avversario e messaggio di log
        """
        danno = 0
        msg = ""
        if self.esegui_azione():
            danno = random.randint(
                self.attacco_min, self.attacco_max
            ) + mod_ambiente
            if danno < 0:
                danno = 0
                msg = (
                    f"{self.nome} lancia un incantesimo, ma non "
                    f"infligge danni!"
                )
            else:
                msg = (
                    f"{self.nome} lancia un incantesimo infliggendo "
                    f"{danno} danni!"
                )
        else:
            msg = f"{self.nome} tenta di attaccare ma fallisce!"
        logger.info(msg)
        print(msg)
        return danno, msg


@dataclass
class Guerriero(Personaggio):
    """
    Classe che rappresenta un personaggio guerriero.
    Estende la classe Personaggio, con salute_max di 120, attacco piu potente e
    guarigione post duello fissa di 30 salute
    """

    salute_max: int = 130
    salute: int = salute_max
    attacco_min: int = 20
    attacco_max: int = 100
    iniziativa: int = 20

    def attacca(self, mod_ambiente: int = 0) -> tuple[int, str]:
        """
        Il Guerriero ha un attacco minimo aumentato di 15*  e un attacco
        massimo aumentato di 20* + il modificatore dell'ambiente corrente
        * rispetto ai campi della classe Personaggio

        Args:
            bersaglio (Personaggio): personaggio che subisce l'attacco
            mod_ambiente (int): modificatore ambientale di attacco (default: 0)

        Returns:
            tuple[int, str]: danno inflitto all'avversario e messaggio di log
        """
        danno = 0
        msg = ""
        if self.esegui_azione():
            danno = random.randint(
                self.attacco_min, self.attacco_max
            ) + mod_ambiente
            if danno < 0:
                danno = 0
                msg = (
                    f"{self.nome} colpisce, ma non "
                    f"infligge danni!"
                )
            else:
                msg = (
                    f"{self.nome} colpisce con la spada infliggendo "
                    f"{danno} danni!"
                )
        else:
            msg = f"{self.nome} tenta di attaccare ma fallisce!"
        logger.info(msg)
        print(msg)
        return danno, msg

@dataclass
class Ladro(Personaggio):
    """
    Estende la classe Personaggio, ha salute elevata a 140, +5 attacco_max e
    attacco_min, recupera punti salute al termine del duello
    casualmente in un range 10-40
    """
    salute_max: int = 120
    salute: int = salute_max
    attacco_max: int = 85
    attacco_min: int = 10
    iniziativa: int = 25


    def attacca(self, mod_ambiente: int = 0) -> tuple[int, str]:
        """
        attacco del ladro valore random tra attacco_min e attacco_max
        con un modificatore ambientale, se l'azione ha successo

        Args:
            mod_ambiente (int): modificatore ambientale di attacco (default: 0)

        Returns:
            tuple[int, str]: danno inflitto all'avversario e messaggio di log
        """
        danno = 0
        if self.esegui_azione():
            danno = random.randint(
                self.attacco_min, self.attacco_max
            ) + mod_ambiente
            if danno < 0:
                danno = 0
                msg = (
                    f"{self.nome} colpisce, ma non "
                    f"infligge danni!"
                )
            else:
                msg = (
                    f"{self.nome} colpisce furtivamente infliggendo "
                    f"{danno} danni!"
                )
        else:
            msg = f"{self.nome} tenta di attaccare ma fallisce!"
        logger.info(msg)
        return danno, msg
