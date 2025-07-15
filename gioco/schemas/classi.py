from marshmallow import Schema, fields, post_load
from gioco.classi import Personaggio, Mago, Guerriero, Ladro
import uuid

class PersonaggioSchema(Schema):
    """
    Schema per la serializzazione/deserializzazione dei personaggi.
    Utilizza Marshmallow per definire i campi e le loro proprietà.
    """
    classe = fields.String(required=True)
    id = fields.UUID(load_default=lambda: uuid.uuid4())

    storico_danni_subiti = fields.List(fields.Integer(), load_default=list)

    def _set_default_if_empty(self, data, key, default):
        """
        Imposta un valore di default per il campo 'key' se il campo è assente o vuoto.
        """
        if key not in data or data[key] in (None, '', [], {}):
            data[key] = default

    @post_load
    def make_personaggio(self, data, **kwargs):
        print(f"\nimport: \n{data}\n")
        classe = data.get("classe", "Personaggio")
        # Rimuovi il campo 'classe' dai dati prima di creare l'istanza
        data_clean = {k: v for k, v in data.items() if k != "classe"}

        if classe == "Mago":
            # Applica i default specifici del Mago se i campi sono assenti o vuoti
            self._set_default_if_empty(data_clean, "salute_max", 80)
            self._set_default_if_empty(data_clean, "salute", 80)
            self._set_default_if_empty(data_clean, "attacco_min", 0)
            self._set_default_if_empty(data_clean, "attacco_max", 90)
            char = Mago(**data_clean)
            char.classe = classe
            return char
        elif classe == "Guerriero":
            # Applica i default specifici del Guerriero se i campi sono assenti o vuoti
            self._set_default_if_empty(data_clean, "salute_max", 120)
            self._set_default_if_empty(data_clean, "salute", 120)
            self._set_default_if_empty(data_clean, "attacco_min", 20)
            self._set_default_if_empty(data_clean, "attacco_max", 100)
            char = Guerriero(**data_clean)
            char.classe = classe
            return char
        elif classe == "Ladro":
            # Applica i default specifici del Ladro se i campi sono assenti o vuoti
            self._set_default_if_empty(data_clean, "salute_max", 100)
            self._set_default_if_empty(data_clean, "salute", 100)
            self._set_default_if_empty(data_clean, "attacco_min", 10)
            self._set_default_if_empty(data_clean, "attacco_max", 85)
            char = Ladro(**data_clean)
            char.classe = classe
            return char
        else:
            # Applica i default generici del Personaggio se i campi sono assenti o vuoti
            self._set_default_if_empty(data_clean, "salute_max", 200)
            self._set_default_if_empty(data_clean, "salute", 100)
            self._set_default_if_empty(data_clean, "attacco_min", 5)
            self._set_default_if_empty(data_clean, "attacco_max", 80)
            return Personaggio(**data_clean)
