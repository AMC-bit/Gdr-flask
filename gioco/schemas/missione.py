import json
import os
import uuid
from marshmallow import Schema, fields, post_load

from gioco.schemas.ambiente import AmbienteSchema
from gioco.missione import Missione
from gioco.schemas.oggetto import OggettoSchema
from gioco.schemas.personaggio import PersonaggioSchema
from gioco.schemas.strategy import StrategiaSchema
from gioco.schemas.ambiente import AmbienteSchema

class MissioniSchema(Schema):
    id = fields.UUID(load_default=lambda: uuid.uuid4())
    nome = fields.String(required=True)
    ambiente = fields.Nested(AmbienteSchema, required=True)
    nemici = fields.List(fields.Nested(PersonaggioSchema), required=True)
    premi = fields.List(fields.Nested(OggettoSchema), required=True)
    strategia_nemici = fields.Nested(StrategiaSchema, allow_none=True)
    completata = fields.Bool()
    attiva = fields.Bool()

    @post_load
    def make_Missioni(self, data, **kwargs) -> Missione:
        return Missione(**data)
