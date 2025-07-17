import json


class Json:

    @staticmethod
    def scrivi_dati(file_path: str, dati_da_salvare: dict) -> None:
        """
        Scrive i dati in un file JSON.

        Args:
            file_path (str): Percorso del file in cui salvare i dati.
            dati_da_salvare (dict): Dati da salvare nel file JSON.
            encoder (function): Funzione di codifica per convertire oggetti in JSON.

        Return:
            None
        """

        try:
            with open(file_path, 'w', encoding="utf-8") as file:
                json.dump(dati_da_salvare, file, indent=4)
            print(f"Dati scritti con successo in {file_path}")
        except Exception as e:
            print(f"Errore nella scrittura del file JSON: {e}")

    @staticmethod
    def carica_dati(file_path: str) -> dict:
        """
        Carica i dati da un file JSON specificato.

        Args:
            file_path (str): Percorso del file da cui caricare i dati.

        Returns:
            dict: Dati caricati dal file JSON.
        """

        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                dati = json.load(file)
            return dati
        except Exception as e:
            print(f"Errore nella lettura del file JSON: {e}")
            return None
