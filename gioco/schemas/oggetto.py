from marshmallow import fields, Schema

class OggettoSchema(Schema):
    nome = fields.Str()
    usato = fields.Bool()
    valore = fields.Int()
    tipo_oggetto = fields.Str()
    classe = fields.Str(required=True)
