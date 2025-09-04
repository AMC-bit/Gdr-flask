# Presentazioni: Standard per la documentazione, Docstring e Sphinx (Konrad)

Questo file contiene due versioni della presentazione: una da 5 minuti e 30 secondi e una da 5 minuti.

---

## Versione 1 — Presentazione completa (5 minuti e 30 secondi)

### Introduzione (30 secondi)

Buongiorno, oggi vi parlerò degli standard per la documentazione adottati nel nostro progetto "Saltatio Mortis".

Nel nostro team abbiamo dovuto affrontare una sfida comune: come mantenere traccia di ciò che dovevamo implementare e di quello che avevamo già sviluppato, evitando confusione tra i membri del team.

La nostra soluzione è stata adottare un approccio professionale basato su **Sphinx** e **docstring in stile Google**, che garantisce documentazione automatica, coerente e facilmente mantenibile per tutto il codice.

### Sphinx: Il Motore della Documentazione (2 minuti)

Sphinx è molto più di un semplice generatore di documentazione: è un ecosistema completo che trasforma il nostro codice Python in documentazione web navigabile e professionale.

La caratteristica fondamentale di Sphinx è che non si limita a leggere i commenti nel codice. Attraverso il meccanismo di **importazione dinamica**, Sphinx esegue effettivamente il nostro codice Python per estrarre informazioni dettagliate su classi, metodi, parametri e type hints. Questo significa che ogni volta che modifichiamo una funzione, la documentazione si aggiorna automaticamente senza intervento manuale.

Nel nostro progetto, la configurazione in `conf.py` è cruciale. La riga più importante è:

```python
import os, sys
# Sphinx "vede" il nostro codice grazie a questo path
sys.path.insert(0, os.path.abspath('..'))
```

Questa riga dice a Sphinx dove trovare il nostro package `saltatio_mortis`, permettendogli di importare tutti i moduli.

Le estensioni sono il cuore del sistema e ne abbiamo configurate tre fondamentali:

- **autodoc**: scansiona il codice Python, importa i moduli ed estrae automaticamente firme delle funzioni, docstring e metadati
- **napoleon**: traduce le nostre docstring in stile Google nel formato reStructuredText che Sphinx comprende nativamente
- **sphinx_autodoc_typehints**: legge i type hints Python e li integra elegantemente nella documentazione finale

### Standard DocString: Stile Google in Italiano (2 minuti)

Abbiamo adottato lo stile Google per la sua leggibilità e il supporto nativo in Sphinx. Tra i vari formati disponibili (Sphinx nativo, NumPy, Google), quello Google offre il miglior equilibrio tra leggibilità nel codice sorgente e ricchezza informativa.

Abbiamo fatto la scelta consapevole di scrivere le docstring in italiano per:

1. Coerenza linguistica (team e contesto italiano)
2. Accessibilità per tutti i membri del team
3. Terminologia del dominio (personaggio, missione, inventario) più naturale

Esempio pratico dal nostro codice:

```python
def usa_inventario_automatico(
    inventario: Inventario,
    pg: Personaggio,
    missione: Missione,
    bersagli: list[Personaggio],
    strategia: Strategia | None = None,
) -> tuple[int | None, str]:
    """
    Utilizza un oggetto dall'inventario in modo automatico.

    Args:
        inventario (Inventario): L'inventario da cui utilizzare l'oggetto.
        pg (Personaggio): Il personaggio che utilizza l'oggetto.
        missione (Missione): La missione corrente.
        bersagli (list[Personaggio]): I bersagli dell'effetto dell'oggetto.
        strategia (Strategia, optional): Strategia da utilizzare.

    Returns:
        tuple[int | None, str]: Il risultato dell'uso dell'oggetto e messaggio descrittivo.
    """
```

Ogni docstring segue una struttura standard: descrizione concisa, parametri con tipo e descrizione, cosa restituisce, ed eventuali eccezioni.

### Type Hints e Automazione (30 secondi)

I type hints sono metadati che Sphinx utilizza per arricchire la documentazione.

Sphinx con i type hints:

- Valida la coerenza tra documentazione e tipi dichiarati
- Genera collegamenti automatici tra classi correlate
- Mostra i tipi in modo elegante nella documentazione finale

Il processo è automatico: Sphinx scansiona i file, importa i moduli, estrae docstring e type hints e genera HTML navigabile con ricerca.

### Benefici e Conclusioni (30 secondi)

Benefici principali:

1. Manutenibilità: documentazione sempre aggiornata con il codice
2. Professionalità: standard industriale, navigazione intuitiva, output moderno
3. Collaborazione: standard condiviso, onboarding più facile, code review efficaci
4. Coerenza: formato uniforme e gerarchie di classe chiare

Conclusione: Sphinx con docstring Google ha trasformato la documentazione in una "finestra vivente" sul codice, automatizzata, coerente e professionale.

---

## Versione 2 — Presentazione ridotta (5 minuti)

### Introduzione (45 secondi)

Buongiorno, oggi vi parlerò degli standard per la documentazione adottati nel nostro progetto "Saltatio Mortis".

Per evitare confusione e allineare il team, abbiamo adottato **Sphinx** con **docstring in stile Google** per ottenere documentazione automatica e sempre aggiornata.

### Sphinx: Il Sistema di Documentazione (2 minuti)

Sphinx trasforma il codice Python in documentazione web navigabile ed esegue **importazione dinamica** del codice per estrarre firme, docstring e type hints. Ogni modifica al codice aggiorna la documentazione.

Configurazione chiave in `conf.py`:

```python
import os, sys
sys.path.insert(0, os.path.abspath('..'))
```

Estensioni principali:

- **autodoc** (import e estrazione automatica)
- **napoleon** (docstring Google)
- **sphinx_autodoc_typehints** (integrazione type hints)

### DocString in Stile Google (1 minuto e 30 secondi)

Scelto per equilibrio tra leggibilità e completezza. Docstring in italiano per coerenza e chiarezza di dominio.

Esempio sintetico:

```python
def usa_inventario_automatico(
    inventario: Inventario,
    pg: Personaggio,
    strategia: Strategia | None = None,
) -> tuple[int | None, str]:
    """
    Utilizza un oggetto dall'inventario in modo automatico.

    Args:
        inventario (Inventario): Fonte dell'oggetto.
        pg (Personaggio): Utilizzatore.
        strategia (Strategia, optional): Strategia da applicare.

    Returns:
        tuple[int | None, str]: Risultato e messaggio.
    """
```

Struttura essenziale: descrizione, Args, Returns, (Raises quando serve).

### Type Hints e Automazione (45 secondi)

I type hints permettono collegamenti automatici e coerenza. Processo in 4 passi: scansiona file, importa moduli, estrae docstring e type hints, genera HTML con ricerca.

### Benefici e Chiusura (45 secondi)

1. Zero manutenzione manuale
2. Standard professionale con ricerca
3. Collaborazione più semplice
4. Coerenza di formato

Conclusione: documentazione come "finestra vivente" che evolve con il progetto.
