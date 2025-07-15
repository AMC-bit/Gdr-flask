from marshmallow import fields, Schema, post_load
from gioco.ambiente import Ambiente

def get_all_subclasses(cls):
    """
    Ottiene tutte le sottoclassi di una classe base, utilizzata per
    la deserializzazione dinamica tramite Marshmallow.

    Args:
        cls: La classe base di cui ottenere le sottoclassi

    Returns:
        set: Un set contenente tutte le sottoclassi
    """
    subclasses = set()
    for subclass in cls.__subclasses__():
        subclasses.add(subclass)
        # subclasses.update(get_all_subclasses(subclass))
        # nel caso di sottoclassi indirette
    return subclasses

class AmbienteSchema(Schema):
    classe = fields.String(required=True)
    nome = fields.String(required=True)
    mod_attacco = fields.Integer()
    mod_cura = fields.Float()

    @post_load
    def make_obj(self, data, **kwargs):
        # Crea la mappa dinamica: nome classe -> classe Python
        classe_nome = data.get("classe")
        ambienti_map = {
            subcls.__name__: subcls
            for subcls in get_all_subclasses(Ambiente)
        }

        # rimuovo classe dai dati per evitare conflitti
        data_clean = {k: v for k, v in data.items() if k != 'classe'}

        if classe_nome in ambienti_map:
            ambiente_cls = ambienti_map[classe_nome]
            return ambiente_cls(**data_clean)
        else:
            # Fallback alla classe base Ambiente
            return Ambiente(**data_clean)

    def dump(self, obj, *, many=None, **kwargs):
        """
        Override del metodo dump per aggiungere automaticamente il campo classe
        """
        # Ottieni i dati base dall'oggetto usando il metodo parent
        data = super().dump(obj, many=many, **kwargs)

        if many:
            # Se stiamo serializzando una lista di oggetti
            if isinstance(obj, (list, tuple)) and isinstance(data, list):
                for i, item_data in enumerate(data):
                    if i < len(obj) and hasattr(obj[i], '__class__'):
                        item_data['classe'] = obj[i].__class__.__name__
        else:
            # Se stiamo serializzando un singolo oggetto
            if isinstance(data, dict) and hasattr(obj, '__class__'):
                data['classe'] = obj.__class__.__name__

        return data
