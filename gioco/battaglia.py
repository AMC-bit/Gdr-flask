import random
from gioco.ambiente import AmbienteFactory
from gioco.classi import Guerriero, Ladro, Mago
from gioco.strategy import StrategiaAttacco, StrategiaAttaccoFactory as SAF
from utils.messaggi import Messaggi
from utils.salvataggio import SerializableMixin
from utils.log import Log
from gioco.personaggio import Personaggio
from gioco.oggetto import BombaAcida, Medaglione, Oggetto, PozioneCura
from gioco.inventario import Inventario
from gioco.missione import Missione


@SerializableMixin.register_class
class Battaglia(SerializableMixin):
    """_summary_
    """
    def __init__(self, missione: Missione, giocatori: list[tuple[Personaggio, Inventario]]) -> None:
        self.missione = missione
        self.giocatori_tupla = giocatori
        self.ambiente = missione.ambiente
        self.nemici_lista = missione.nemici
        self.nemici_tupla = self.setup_nemici(self.nemici_lista)
        self.giocatori_lista = [x[0] for x in giocatori]
        self.personaggi = self.giocatori_lista + self.nemici_lista
        self.personaggi = self.ordine_combattimento(self.personaggi)
        turno_in_corso = 0

    def crea_inventario_base(self, proprietario: Personaggio) -> Inventario:
        inventario = Inventario(proprietario=proprietario)
        inventario._aggiungi(PozioneCura())
        inventario._aggiungi(BombaAcida())
        inventario._aggiungi(Medaglione())
        return inventario

    def setup_nemici(self, lista_nemici: list[Personaggio]) -> list[tuple[Personaggio, Inventario, StrategiaAttacco]]:
        nemici_preparati = []
        for nemico in lista_nemici:
            strategia = SAF.strategia_random()
            inventario = self.crea_inventario_base(nemico)
            nemici_preparati.append((nemico, inventario, strategia))
        return nemici_preparati

    def ordine_combattimento(
        self,
        personaggi: list[Personaggio] = None
    ) -> list[Personaggio]:
        """
        Ordina i personaggi giocanti e in maniera randomica.
        Il metodo genera un valore (compreso tra 1 e 5*len(personaggi) )
        per ciascuno dei personaggi e li ordina in base a questo valore.
        I personaggi di tipo Guerriero, Mago e Ladro hanno
        un bonus di iniziativa rispettivamente di 2, 0 e 4.
        In caso di parità per il secondo personaggio
        l'iniziativa viene ritirata.


        Args:
            list[Personaggio] personaggi: Lista dei personaggi
            da ordinare. Se non viene specificata, viene usata
            la lista dei personaggi del turno.

        Returns:
            list[Personaggio]: Lista dei personaggi ordinati per
            il tiro di iniziativa.
        """
        if personaggi is None:
            personaggi = self.personaggi

        lista_per_iniziativa = []

        for personaggio in personaggi:
            if isinstance(personaggio, Guerriero):
                bonus_iniziativa = 2
            elif isinstance(personaggio, Mago):
                bonus_iniziativa = 0
            elif isinstance(personaggio, Ladro):
                bonus_iniziativa = 4

            while True:
                iniziativa = random.randint(1, 5 * len(personaggi))
                iniziativa += bonus_iniziativa
                if iniziativa not in [x[0] for x in lista_per_iniziativa]:
                    lista_per_iniziativa.append((personaggio, iniziativa))
                    break

        lista_per_iniziativa.sort(key=lambda x: x[0])
        return [p for _, p in lista_per_iniziativa]

    def get_personaggio(self, turno: int = None) -> Personaggio:
        """
        Restituisce il personaggio attivo per il turno specificato.
        se il turno non è specificato, usa il turno corrente della istanza.

        Args:
            turno (int): Il numero del turno corrente.

        Returns:
            Personaggio: Il personaggio attivo per il turno.
        """
        if turno is None:
            turno = self.turno_in_corso
        if turno < 0 or turno >= len(self.personaggi):
            Messaggi.add_to_messaggi("ERRORE!!!\nTurno fuori intervallo.")
        return self.personaggi[turno]

    def importa_ambiente(self, scelta_ambiente: str) -> None:
        """
        Imposta o reimposta l'ambiente della battaglia in base alla stringa fornita.
        Se l'ambiente è "Foresta", "Vulcano" o "Palude", imposta l'ambiente
        corrispondente. Se l'ambiente è un numero (1, 2 o 3),
        imposta l'ambiente corrispondente a quel numero.

        Args:
            scelta_ambiente (str):
        """
        if scelta_ambiente == "Foresta":
            scelta = "1"
        elif scelta_ambiente == "Vulcano":
            scelta = "2"
        elif scelta_ambiente == "Palude":
            scelta = "3"
        elif scelta_ambiente in ["1", "2", "3"]:
            scelta = scelta_ambiente
        else:
            Messaggi.add_to_messaggi("opzione non prevista")
            return
        self.ambiente = AmbienteFactory.seleziona_da_id(scelta)
        Messaggi.add_to_messaggi(f"Ambiente impostato: {self.ambiente.nome}")

    def azione_esegui_attacco(self, turno_bersaglio: int) -> None:
        """
        Esegue l'attacco del personaggio attivo contro il bersaglio specificato.
        Il personaggio attivo è determinato dal turno corrente (il turno corrisponde alla ).


        Args:
            turno_bersaglio (int): _description_
        Returns:
            None
        """
        attaccante = self.get_personaggio(self.turno_in_corso)
        bersaglio = self.get_personaggio(turno_bersaglio)
        attaccante.attacca(
            bersaglio,
            mod_ambiente=self.ambiente.modifica_attacco_max(attaccante) if self.ambiente else 0
        )
        Messaggi.add_to_messaggi(f"{attaccante.nome} attacca {bersaglio.nome}!")
        self.avanza_turno() # Avanza al turno successivo dopo l'attacco da calcolare se mantenerlo o meno

    def azione_usa_oggetto(self, nome_oggetto: str, turno_utilizzatore: int = None, turno_bersaglio: int = None) -> None:
        """
        Usa un oggetto specificato dal nome sull'attuale personaggio attivo o su un bersaglio specificato.
        Se il bersaglio non è specificato, l'oggetto viene usato sul personaggio attivo.

        Args:
            nome_oggetto (str): Il nome dell'oggetto da usare.
            turno_bersaglio (int, optional): Il turno del personaggio bersaglio. Defaults to None.

        Returns:
            None
        """
        if turno_utilizzatore is None:
            utilizzatore = self.get_personaggio()
        else:
            utilizzatore = self.get_personaggio(turno_utilizzatore)
        inventario = Inventario()
        if utilizzatore in self.giocatori_tupla:
            inventario = self.giocatori_tupla[1]
        elif utilizzatore in self.nemici_tupla:
            inventario = self.nemici_tupla[1]
        oggetto = inventario.cerca_oggetto_by_name(nome_oggetto)

        if oggetto is None:
            Messaggi.add_to_messaggi(f"{utilizzatore.nome} non ha l'oggetto {nome_oggetto}.")
            return

        if turno_bersaglio is not None:
            bersaglio = self.get_personaggio(turno_bersaglio)
            oggetto.usa(bersaglio, ambiente=self.ambiente)
            Messaggi.add_to_messaggi(f"{utilizzatore.nome} usa {nome_oggetto} su {bersaglio.nome}.")
        else:
            oggetto.usa(utilizzatore, ambiente=self.ambiente)
            Messaggi.add_to_messaggi(f"{utilizzatore.nome} usa {nome_oggetto}.")

    def azione_cura(self, turno_pg: int = None) -> None:
        """
        Esegue l'azione di cura per il personaggio attivo.
        Se il turno non è specificato, usa il turno corrente della istanza.

        Args:
            turno_utilizzatore (int, optional): è il turno del personaggio che esegue l'azione di cura.
        Returns:
            None
        """
        if turno_pg is None:
            utilizzatore = self.get_personaggio()
        else:
            utilizzatore = self.get_personaggio(turno_pg)

        mod_ambiente = self.ambiente.modifica_cura(utilizzatore) if self.ambiente else 0
        utilizzatore.recupera_salute(mod_ambiente=mod_ambiente)

    def avanza_turno(self) -> None:
        """
        Avanza al turno successivo, passando al prossimo personaggio
        nella lista dei personaggi. Se si raggiunge la fine della lista,
        il turno viene riportato al primo personaggio.
        Se il personaggio che dovrebbe essere attivo è sconfitto,
        si salta al prossimo personaggio non sconfitto.
        se per assurdo tutti i personaggi
        Args:
            None
        Returns:
            None
            str: "end" se tutti i personaggi sono sconfitti.
        """
        for _ in range(len(self.personaggi)):
            self.turno_in_corso = (self.turno_in_corso + 1) % len(self.personaggi)
            if not self.get_personaggio(self.turno_in_corso).sconfitto():
                return
        Messaggi.add_to_messaggi("Tutti i personaggi sono stati sconfitti.")
        return "end"

    def cambio_turno(self, turno: int) -> None:
        """
        Cambia il turno corrente al turno specificato.
        Se il turno specificato è fuori intervallo, non cambia il turno.

        Args:
            turno (int): Il numero del turno da impostare.

        Returns:
            None
        """
        if 0 <= turno < len(self.personaggi):
            self.turno_in_corso = turno
            if self.get_personaggio(turno).sconfitto():
                self.avanza_turno()
        else:
            Messaggi.add_to_messaggi("ERRORE!!!\nTurno fuori intervallo.")

    def inizia_battaglia(self) -> bool:
        """
        Inizia la battaglia tra i personaggi giocanti e i nemici.
        Gestisce i turni, gli attacchi e le azioni fino alla conclusione della battaglia.

        Returns:
            bool: True se la battaglia è vinta dai personaggi giocanti, False se sono sconfitti.
        """
        self.counter_turni = 0
        if self.missione is None:
            Messaggi.add_to_messaggi("Inizio della battaglia.")
        else:
            Messaggi.add_to_messaggi(f"inizio della missione: {self.missione.nome}")
        Messaggi.add_to_messaggi(f"Ambiente: {self.ambiente.nome if self.ambiente else 'Nessun ambiente'}")
        Messaggi.add_to_messaggi(f"Personaggi giocanti: {[p.nome for p in self.giocatori_lista]}")
        Messaggi.add_to_messaggi(f"Nemici: {[n.nome for n in self.nemici_lista]}")

        # Inizializza il turno corrente
        self.turno_in_corso = 0

        # Loop principale della battaglia

    def status_scontro(self) -> None:
        """
        restituisce lo stato del combattimento qualora sia vinto o perso.

        Returns:
            None:
        """
        if self.missione is not None:
            tutti_giocatori_sconfitti = all(giocatore.sconfitto() for giocatore in self.giocatori_lista)
            tutti_nemici_sconfitti = all(nemico.sconfitto() for nemico in self.nemici_lista)

            if tutti_giocatori_sconfitti:
                Messaggi.add_to_messaggi("Stato del combattimento: perso.")
            elif tutti_nemici_sconfitti:
                Messaggi.add_to_messaggi("Stato del combattimento: vinto.")
            else:
                Messaggi.add_to_messaggi("Stato del combattimento: in corso.")
        return