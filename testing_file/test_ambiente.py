#!/usr/bin/env python3
"""Test rapido per la deserializzazione dell'ambiente"""

import sys
import os
from gioco.ambiente import AmbienteSchema

# Aggiungi il percorso del progetto al sys.path
sys.path.insert(0, os.path.dirname(__file__))


def test_ambiente():
    """Test deserializzazione ambiente dal file imboscata.json"""
    ambiente_data = {
        "classe": "Foresta",
        "nome": "Foresta",
        "mod_attacco": 5,
        "mod_cura": 5.5
    }

    try:
        schema = AmbienteSchema()
        ambiente = schema.load(ambiente_data)

        print(f"✓ Ambiente deserializzato: {type(ambiente).__name__}")
        print(f"  - Nome: {ambiente.nome}")
        print(f"  - Classe: {getattr(ambiente, 'classe', 'N/A')}")
        print(f"  - Mod attacco: {ambiente.mod_attacco}")
        print(f"  - Mod cura: {ambiente.mod_cura}")

        return True

    except Exception as e:
        print(f"✗ Errore nella deserializzazione ambiente: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Test deserializzazione ambiente\n")
    success = test_ambiente()
    print(f"\nRisultato: {'✓ SUCCESSO' if success else '✗ FALLITO'}")
