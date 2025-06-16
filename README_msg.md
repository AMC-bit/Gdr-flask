# Task per i msg e il passaggio ai template

- Scegli una classe, comunicalo agli altri
- Aggiungi alla classe una proprietà str che chiameremo messaggi
- dentro ogni metodo della classe concatenare a messaggi tutti i msg andando a capo a ogni nuovo msg usando \n
- vanno anche concatenati a messaggi tutti i messaggi che vengono sollevati dalle eccezioni e che siano pertinenti al giocatore

```python
    def add_to_messaggi(self, msg:str):
        """
        Aggiunge un nuovo msg a messaggi, mandando a capo ad ogni nuovo msg

        Args:
            msg (str): nuovo msg da concatenare
        """
        if self.messaggi=="" :
            self.messaggi=msg
        else:
            self.messaggi = f"{self.messaggi}\n{msg}"

    def get_messaggi(self):
        return self.messaggi

    def delete_messaggi(self):
        self.messaggi=""
```

- vanno anche concatenati a messaggi tutti i messaggi che vengono sollevati dalle eccezioni e che siano pertinenti al giocatore