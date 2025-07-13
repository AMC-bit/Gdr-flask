#!/usr/bin/env python3
"""Test per verificare che gli ID delle missioni siano deterministici"""

import sys
import os
from gioco.schemas.missione import GestoreMissioniSchema

# Aggiungi il percorso del progetto al sys.path
sys.path.insert(0, os.path.dirname(__file__))


def test_id_deterministici():
    """
    Test per verificare che gli ID delle missioni siano gli stessi
    ad ogni caricamento
    """
    print("=== Test ID Deterministici ===")

    # Carica il gestore per la prima volta
    gestore1 = GestoreMissioniSchema().crea_GestoreMissioni_Statico()
    missioni1 = {
        missione.nome: str(missione.id) for missione in gestore1.lista_missioni
        }

    print("Prima chiamata:")
    for nome, id_missione in missioni1.items():
        print(f"  {nome}: {id_missione}")

    # Carica il gestore per la seconda volta
    gestore2 = GestoreMissioniSchema().crea_GestoreMissioni_Statico()
    missioni2 = {
        missione.nome: str(missione.id) for missione in gestore2.lista_missioni
        }

    print("\nSeconda chiamata:")
    for nome, id_missione in missioni2.items():
        print(f"  {nome}: {id_missione}")

    # Verifica che gli ID siano gli stessi
    print("\n=== Confronto ===")
    consistent = True
    for nome in missioni1:
        if nome in missioni2:
            id1 = missioni1[nome]
            id2 = missioni2[nome]
            if id1 == id2:
                print(f"✓ {nome}: {id1} (STESSO)")
            else:
                print(f"✗ {nome}: {id1} vs {id2} (DIVERSO)")
                consistent = False
        else:
            print(f"✗ {nome}: presente solo nella prima chiamata")
            consistent = False

    return consistent


def test_serializzazione_sessione():
    """
    Test per verificare che la serializzazione/deserializzazione
    dalla sessione mantenga gli ID
    """
    print("\n=== Test Serializzazione Sessione ===")

    schema = GestoreMissioniSchema()

    # Carica il gestore
    gestore_orig = schema.crea_GestoreMissioni_Statico()
    id_originali = {
        missione.nome:
            str(missione.id) for missione in gestore_orig.lista_missioni
        }

    print("ID originali:")
    for nome, id_missione in id_originali.items():
        print(f"  {nome}: {id_missione}")

    # Serializza (simula salvataggio in sessione)
    gestore_dict = schema.dump(gestore_orig)

    # Deserializza (simula caricamento da sessione)
    gestore_restored = schema.load(gestore_dict)
    id_restored = {
        missione.nome:
            str(missione.id) for missione in gestore_restored.lista_missioni
        }

    print("\nID dopo serializzazione/deserializzazione:")
    for nome, id_missione in id_restored.items():
        print(f"  {nome}: {id_missione}")

    # Verifica consistenza
    print("\n=== Confronto ===")
    consistent = True
    for nome in id_originali:
        if nome in id_restored:
            id_orig = id_originali[nome]
            id_rest = id_restored[nome]
            if id_orig == id_rest:
                print(f"✓ {nome}: {id_orig} (MANTIENE ID)")
            else:
                print(f"✗ {nome}: {id_orig} vs {id_rest} (CAMBIATO)")
                consistent = False

    return consistent


if __name__ == "__main__":
    print("Test consistenza ID missioni\n")

    # Esegui i test
    id_deterministici = test_id_deterministici()
    sessione_ok = test_serializzazione_sessione()

    print("\n=== RISULTATI FINALI ===")
    if id_deterministici and sessione_ok:
        print("✅ Tutti i test sono passati!")
        print("  - Gli ID delle missioni sono deterministici")
        print("  - La serializzazione/deserializzazione mantiene gli ID")
    else:
        print("❌ Alcuni test sono falliti")
        if not id_deterministici:
            print("  - Gli ID cambiano ad ogni caricamento")
        if not sessione_ok:
            print(
                "  - La serializzazione/deserializzazione non mantiene gli ID"
            )
