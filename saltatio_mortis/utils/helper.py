
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
        subclasses.update(get_all_subclasses(subclass))
        # nel caso di sottoclassi indirette
    return subclasses