from marshmallow import fields, Schema, post_load
from utils.helper import get_all_subclasses
import uuid

class OggettoSchema(Schema):
    id = fields.UUID(load_default=lambda: uuid.uuid4())
    nome = fields.Str()
    usato = fields.Bool()
    valore = fields.Int()
    tipo_oggetto = fields.Str()
    classe = fields.Str(required=True)

    @post_load
    def make_oggetto(self, data, **kwargs):
        from gioco.oggetto import Oggetto

        # Crea la mappa dinamica: nome classe -> classe Python
        classe_nome = data.get("classe")
        oggetti_map = {
            subcls.__name__: subcls
            for subcls in get_all_subclasses(Oggetto)
        }

        if classe_nome in oggetti_map:
            oggetto_cls = oggetti_map[classe_nome]
            # Rimuovi il campo 'classe' dai data prima di passarli
            # al costruttore
            data_copy = data.copy()
            data_copy.pop('classe', None)
            return oggetto_cls(**data_copy)
        else:
            # Fallback alla classe base Oggetto
            return Oggetto(**data)
