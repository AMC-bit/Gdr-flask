
from marshmallow import Schema, fields, post_load
import uuid

from gioco.personaggio import Personaggio



class PersonaggioSchema(Schema):
    """
    Schema per la serializzazione/deserializzazione dei personaggi.
    Utilizza Marshmallow per definire i campi e le loro proprietà.
    """
    classe = fields.String(required=True)
    id = fields.UUID(dump_only=True)
    nome = fields.String(required=True)
    npc = fields.Boolean(load_default=True)
    salute_max = fields.Integer()
    salute = fields.Integer()
    attacco_min = fields.Integer()
    attacco_max = fields.Integer()
    livello = fields.Integer(load_default=1)
    destrezza = fields.Integer(load_default=15)
    storico_danni_subiti = fields.List(fields.Integer(), load_default=list)


    @post_load
    def make_personaggio(self, data, **kwargs):
        print(f"\nimport: \n{data}\n")
        return Personaggio(**data)

class MagoSchema(PersonaggioSchema):
    """
    Schema specifico per la classe Mago.
    Estende PersonaggioSchema e aggiunge il campo 'mana'.
    """


class LadroSchema(PersonaggioSchema):
    """
    Schema specifico per la classe Ladro.
    Estende PersonaggioSchema e aggiunge il campo 'destrezza'.
    """
    pass

class GuerrieroSchema(PersonaggioSchema):
    """
    Schema specifico per la classe Guerriero.
    Estende PersonaggioSchema e aggiunge il campo 'forza'.
    """
    pass
