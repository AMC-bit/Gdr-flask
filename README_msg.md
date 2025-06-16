# Task per i msg e il passaggio ai template

- Scegli una classe, comunicalo agli altri
- importa :

```python
    from utils.messaggi import Messaggi
```
- istanzia la classe Messaggio come proprietà static della calsse in modo che sia comune a tutte le istanze della classe
```python
    @SerializableMixin.register_class
class Missione(SerializableMixin):
    messaggi = Messaggi()   #Istanzio Messaggi come proprietà static
    def __init__(self, nome:str, ambiente : Ambiente, nemici : list[Personaggio], premi: list[Oggetto])->None :
        # inizializzazione attributi
        self.nome = nome
        self.ambiente = ambiente  # ereditato dal torneo corrente
        self.nemici = nemici  # lista dei nemici di tutti i tornei
        self.premi = premi  # supporta premio singolo o multiplo
        self.completata = False  # flag per premio in inventario
        self.attiva = False
```
- dentro ogni metodo della classe per concatenare i msg dentro all'oggetto Messaggi usa il metodo add_to_messaggi
```python
    self.messaggi.add_to_messaggi(msg)
```
- vanno anche concatenati a messaggi tutti i messaggi che vengono sollevati dalle eccezioni e che siano pertinenti al giocatore
