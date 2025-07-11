
from marshmallow import Schema, fields, post_load

from gioco.ambiente import AmbienteSchema
from gioco.missione import Missione
from gioco.oggetto import OggettoSchema
from gioco.schemas.personaggio import PersonaggioSchema
from gioco.strategy import StrategiaSchema


class MissioniSchema(Schema):
    id = fields.UUID(dump_only=True)
    nome = fields.String(required=True)
    ambiente = fields.Nested(AmbienteSchema, required=True)
    nemici = fields.List(fields.Nested(PersonaggioSchema), required= True)
    premi = fields.List(fields.Nested(OggettoSchema), required= True)
    strategia = fields.Nested(StrategiaSchema, allow_none=True)
    completata = fields.Bool()
    attiva = fields.Bool()

    @post_load
    def make_Missioni(self, data, **kwargs):
        return Missione(**data)
