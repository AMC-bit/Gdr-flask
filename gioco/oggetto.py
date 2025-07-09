from dataclasses import dataclass, field
from marshmallow import Schema, fields, post_load, validate


@dataclass
class Oggetto:
    """
    Inizializza un oggetto con nome e tipo

    Args:
        nome (str): Nome dell'oggetto

    Returns:
        None

    """
    nome: str
    usato: bool = False
    valore: int = 30
    tipo_oggetto: str = ""
    classe: str = field(init=False)


    def usa(
            self,
            mod_ambiente: int = 0
            ) -> int:
        """
        Metodo da implementare in ogni oggetto

        Args:
            mod_ambiente (int): variabile dell'Ambiente in cui si trova l'oggetto

        Returns:
            int: Valore dell'oggetto usato
        """
        raise NotImplementedError("Questo oggetto non ha effetto definito.")


class OggettoSchema(Schema):
    nome = fields.Str()
    usato = fields.Bool()
    valore = fields.Int()
    tipo_oggetto = fields.Str()
    classe = fields.Str(required=True)


@dataclass
class PozioneCura(Oggetto):
    """
    Cura il personaggio che la usa di un certo valore
    """
    nome: str = "Pozione Rossa"

    def __post_init__(self) -> None:
        """
        Inizializza una pozione di cura

        Args:
            nome (str): Nome della pozione
            valore (int): Valore di cura della pozione
            tipo_oggetto (str): Tipologia di oggetto

        Returns:
            None
        """

        self.valore = 30
        self.classe = "PozioneCura"
        self.tipo_oggetto = "Ristorativo"

    def usa(self, mod_ambiente: int = 0) -> int:
        """
        Cura il personaggio che la usa di un certo valore

        Args:
            mod_ambiente (int): variabile dell'Ambiente in cui si trova l'oggetto

        Returns:
            int: Valore di cura della pozione
        """
        self.usato = True
        return self.valore + mod_ambiente


@dataclass
class BombaAcida(Oggetto):
    """
    Infligge danno pari al valore(Proprietà)
    """
    nome: str = "Bomba Acida"

    def __post_init__(self) -> None:
        """
        Inizializza una bomba acida

        Args:
            nome (str): Nome della bomba
            danno (int): Danno inflitto dalla bomba (dafault: 30)

        Returns:
            None
        """
        self.valore = 30
        self.classe = "BombaAcida"
        self.tipo_oggetto = "Offensivo"

    def usa(self, mod_ambiente: int = 0) -> int:
        """
        Infligge danno al bersaglio
        !!!ATTENZIONE!!!
        Il valore viene passato come un valore negativo!

        Args:
            mod_ambiente (int): variabile dell'Ambiente in cui si trova l'oggetto

        Returns:
            int: Danno inflitto dalla bomba
        """
        self.usato = True
        return - (self.valore + mod_ambiente)


@dataclass
class Medaglione(Oggetto):
    """
    Incrementa l'attacco_max del personaggio che lo usa
    """
    nome: str = "Medaglione"

    def __post_init__(self) -> None:
        """
        Inizializza un medaglione

        Args:
            None

        Returns:
            None
        """
        self.valore = 10
        self.tipo_oggetto = "Buff"
        self.classe = "Medaglione"

    def usa(self, mod_ambiente: int = 0) -> None:
        """
        Incrementa l'attacco_max del personaggio che lo usa

        Args:
            mod_ambiente (int): variabile dell'Ambiente in cui si trova l'oggetto

        Returns:
            None
        """

        self.usato = True
        return int(self.valore + mod_ambiente)
