#!/usr/bin/env python3
"""
Test per verificare la deserializzazione delle missioni con OggettoSchema
aggiornato
"""

import sys
import os
import json
from gioco.schemas.oggetto import OggettoSchema
from gioco.schemas.missione import MissioniSchema

# Aggiungi il percorso del progetto al sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_oggetto_deserializzazione():
    """Test per verificare che OggettoSchema deserializzi correttamente"""
    print("=== Test OggettoSchema ===")

    # Dati di esempio dal file imboscata.json
    oggetto_data = {
        "id": "7e2b1c8a-2e3d-4b7a-9e2a-1c3f4b5d6e7f",
        "nome": "Pozione Rossa",
        "valore": 30,
        "classe": "PozioneCura",
        "tipo_oggetto": "Ristorativo"
    }

    try:
        schema = OggettoSchema()
        oggetto = schema.load(oggetto_data)

        print(f"✓ Oggetto deserializzato: {type(oggetto).__name__}")
        print(f"  - Nome: {oggetto.nome}")
        print(f"  - Classe: {oggetto.classe}")
        print(f"  - Valore: {oggetto.valore}")
        print(f"  - ID: {oggetto.id}")

        return True

    except Exception as e:
        print(f"✗ Errore nella deserializzazione oggetto: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_missione_deserializzazione():
    """Test per verificare che MissioniSchema deserializzi correttamente
    imboscata.json"""
    print("\n=== Test MissioniSchema con imboscata.json ===")

    file_path = "static/mission/imboscata.json"
    if not os.path.exists(file_path):
        print(f"✗ File {file_path} non trovato")
        return False

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        print(f"✓ File JSON caricato: {data.get('nome', 'Sconosciuto')}")

        # Usa MissioniSchema per deserializzare
        schema = MissioniSchema()
        missione = schema.load(data)

        print(f"✓ Missione deserializzata: {missione.nome}")
        print(f"  - Ambiente: {type(missione.ambiente).__name__}")
        print(
            f"  - Nemici: {len(missione.nemici)} "
            f"({[nemico.nome for nemico in missione.nemici]})"
        )
        print(
            f"  - Premi: {len(missione.premi)} "
            f"({[type(premio).__name__ for premio in missione.premi]})"
        )

        return True

    except Exception as e:
        print(f"✗ Errore durante la deserializzazione missione: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Test deserializzazione oggetti e missioni\n")

    success_oggetto = test_oggetto_deserializzazione()
    success_missione = test_missione_deserializzazione()

    print("\n=== RISULTATI ===")
    if success_oggetto and success_missione:
        print("✓ Tutti i test sono passati!")
    else:
        print("✗ Alcuni test sono falliti")
