class Messaggi:
    """
    Gestisce l'accumulo di messaggi (output) da visualizzare sulle pagine html
    """
    def __init__(self):
        self.messaggi_str=""

    def add_to_messaggi(self, msg:str):
        """
        Aggiunge un nuovo msg a messaggi, mandando a capo ad ogni nuovo msg

        Args:
            msg (str): nuovo msg da concatenare
        """
        if self.messaggi_str=="" :
            self.messaggi_str=msg
        else:
            self.messaggi_str = f"{self.messaggi_str}\n{msg}"

    def get_messaggi(self):
        return self.messaggi_str

    def delete_messaggi(self):
        self.messaggi_str=""

#Altra versione questa volta è tutto static , quindi non importa quale classe manda i messaggi vengono tutti raggruppati
class MessaggiStatic:
    messaggi=""

    @staticmethod
    def add_to_messaggi(msg:str):
            """
            Aggiunge un nuovo msg a messaggi, mandando a capo ad ogni nuovo msg

            Args:
                msg (str): nuovo msg da concatenare
            """
            if MessaggiStatic.messaggi == "" :
                MessaggiStatic.messaggi = msg
            else:
                MessaggiStatic.messaggi = f"{MessaggiStatic.messaggi}\n{msg}"
    
    @staticmethod
    def get_messaggi():
        return MessaggiStatic.messaggi
    
    @staticmethod
    def delete_messaggi():
        MessaggiStatic.messaggi=""

