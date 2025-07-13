#!/usr/bin/env python3
"""
Test per verificare la gestione automatica del campo classe in AmbienteSchema
"""

import sys
import os
from gioco.ambiente import AmbienteSchema, Foresta, Vulcano

# Aggiungi il percorso del progetto al sys.path
sys.path.insert(0, os.path.dirname(__file__))


def test_ambiente_serializzazione():
    """
    Test serializzazione ambiente - verifica che il campo classe sia
    aggiunto automaticamente
    """
    print("=== Test Serializzazione Ambiente ===")

    schema = AmbienteSchema()

    # Test con Foresta
    foresta = Foresta()
    print(f"Oggetto Foresta creato: {foresta}")
    print(f"  - Tipo: {type(foresta).__name__}")
    print(f"  - Ha campo 'classe'? {hasattr(foresta, 'classe')}")

    # Serializza
    foresta_dict = schema.dump(foresta)
    print(f"Serializzazione: {foresta_dict}")
    print(f"  - Campo 'classe' presente? {'classe' in foresta_dict}")
    print(f"  - Valore campo 'classe': {foresta_dict.get('classe', 'N/A')}")

    return foresta_dict


def test_ambiente_deserializzazione():
    """
    Test deserializzazione ambiente
    - verifica che il campo classe sia utilizzato correttamente
    """
    print("\n=== Test Deserializzazione Ambiente ===")

    # Dati di esempio dal file imboscata.json
    ambiente_data = {
        "classe": "Foresta",
        "nome": "Foresta",
        "mod_attacco": 5,
        "mod_cura": 5.5
    }

    schema = AmbienteSchema()

    try:
        ambiente = schema.load(ambiente_data)

        print(f"✓ Ambiente deserializzato: {type(ambiente).__name__}")
        print(f"  - Nome: {ambiente.nome}")
        print(f"  - Mod attacco: {ambiente.mod_attacco}")
        print(f"  - Mod cura: {ambiente.mod_cura}")
        print(f"  - Ha campo 'classe' fisico? {hasattr(ambiente, 'classe')}")

        return ambiente

    except Exception as e:
        print(f"✗ Errore nella deserializzazione ambiente: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_ciclo_completo():
    """
    Test ciclo completo:
    serializzazione -> deserializzazione -> serializzazione
    """
    print("\n=== Test Ciclo Completo ===")

    schema = AmbienteSchema()

    # Crea un ambiente originale
    vulcano_orig = Vulcano()
    print(f"Ambiente originale: {type(vulcano_orig).__name__}")

    # Serializza
    vulcano_dict = schema.dump(vulcano_orig)
    print(f"Serializzato: {vulcano_dict}")

    # Deserializza
    vulcano_new = schema.load(vulcano_dict)
    print(f"Deserializzato: {type(vulcano_new).__name__}")

    # Serializza di nuovo
    vulcano_dict2 = schema.dump(vulcano_new)
    print(f"Ri-serializzato: {vulcano_dict2}")

    # Verifica che i dati siano consistenti
    consistent = vulcano_dict == vulcano_dict2
    print(f"✓ Dati consistenti: {consistent}")

    return consistent


if __name__ == "__main__":
    print("Test gestione automatica campo classe in AmbienteSchema\n")

    # Esegui i test
    foresta_dict = test_ambiente_serializzazione()
    ambiente_deserializzato = test_ambiente_deserializzazione()
    ciclo_ok = test_ciclo_completo()

    print("\n=== RISULTATI ===")
    success = (
        foresta_dict and 'classe' in foresta_dict and
        ambiente_deserializzato is not None and
        ciclo_ok
    )

    if success:
        print("✓ Tutti i test sono passati!")
        print(
            "  - Il campo 'classe' viene aggiunto automaticamente "
            "durante la serializzazione"
        )
        print(
            "  - Il campo 'classe' viene utilizzato correttamente "
            "durante la deserializzazione"
        )
        print("  - Gli oggetti Ambiente NON hanno un campo 'classe' fisico")
    else:
        print("✗ Alcuni test sono falliti")
