![banner](saltatio_mortis/static/img/CopertinaRPG.jpg)

<p align='center'>
	<img alt="Static Badge" src="https://img.shields.io/badge/Version-1.0-blue?style=flat">
    <img alt="Last Commit" src="https://img.shields.io/github/last-commit/delectablerec/Gdr-flask?style=flat">
</p>

## Table of Contents

- [Cos'è Saltatio Mortis?](#cosè-saltatio-mortis)
- [Perché lo abbiamo fatto?](#perché-lo-abbiamo-fatto)
- [Features](#features)
- [Bug noti](#bug-noti)
- [Update futuri](#update-futuri)
- [Changelog](#changelog)
- [Come contribuire](#come-contribuire)
- [Team](#team)
- [License](#license)

## Cos'è Saltatio Mortis?
**Saltatio Mortis** è un gioco di ruolo web based a turni di tipo _text-based_, dove il giocatore interagisce con personaggi non giocanti *(NPC)*, completa missioni e utilizza oggetti strategici per progredire nel gioco. Il sistema prevede una gestione avanzata di personaggi, oggetti, missioni e strategie comportamentali degli NPC.

## Perché lo abbiamo fatto?
Il progetto è nato a fini didattici come lavoro di gruppo, ma la scelta del gioco di ruolo si è rivelata ideale perché richiede di costruire un mondo simulato, con regole e comportamenti personalizzati, quasi come una trasposizione codificata della realtà.

Abbiamo trovato tutto ciò un validissimo esercizio che ci ha permesso innanzitutto di sviluppare **capacità logiche**, di **astrazione** e di **collaborazione**, di maturare un approccio alla costante risoluzione dei problemi usando il paradigma della Programmazione ad Oggetti *(OOP)*.

## Features
- Gestione dinamica di `personaggi` con attributi come salute, attacco e destrezza.
- `Oggetti` con comportamenti estendibili via classi derivate.
- `Missioni` strutturate con `ambienti`, nemici e premi.
- `Strategie` di comportamento NPC configurabili per definire stili di gioco aggressivi, difensivi o equilibrati.
- Serializzazione e deserializzazione dei dati tramite *Marshmallow* per facilità di salvataggio e caricamento.

## Bug noti

## Update futuri
- `🟡 In Corso` Possibilità di creare missioni
- `🟡 In Corso` Integrazione con device Raspberry
- `🟡 In Corso` Aggiunta di un pulsante per tornare al menù principale alla fine della battaglia
- Possibilità di gestire autonomamente i turni e gli attacchi grazie a una modalità aggiuntiva di combattimento *"Manuale"*
- Possibilità di curare i propri personaggi una volta finita la battaglia
- Aggiunta di elementi di equipaggiamento dei personaggi (armature, armi)
- Aggiunta nuovi oggetti
- Sistema di recupero dei crediti in base al punteggio ottenuto (+ bonus in caso di vittoria)
- Interfaccia utente migliorata e possibilità di multiplayer
- Engine grafico 2D

## Changelog
Per la lista completa e dettagliata degli aggiornamenti: [CHANGELOG.md](./CHANGELOG.md)


## Come contribuire
Il tuo contributo è importante! Sentiti libero di far crescere il nostro progetto con una pull request con nuove funzionalità, correzioni di bug o miglioramenti.

Se vuoi supportare lo sviluppo e le implementazioni future, dimostraci il tuo sostegno tramite i bottoni qui sotto

[![Star](https://img.shields.io/github/stars/delectablerec/Gdr-flask?style=flat&cacheSeconds=10)](https://github.com/delectablerec/Gdr-flask/stargazers)
[![Fork](https://img.shields.io/github/forks/delectablerec/Gdr-flask?style=flat&cacheSeconds=10)](https://github.com/delectablerec/Gdr-flask/network/members)
[![Watch](https://img.shields.io/github/watchers/delectablerec/Gdr-flask?style=flat&cacheSeconds=10)](https://github.com/delectablerec/Gdr-flask/watchers)

Oppure segui [il creatore del progetto](https://github.com/delectablerec)

[![Followers](https://img.shields.io/github/followers/delectablerec?style=flat&cacheSeconds=10)](https://github.com/delectablerec)

## Team
- Ariotti Matteo
- Chiara Konrad
- Maddaloni Enrico
- Puccini Nicolò
- Fabrice Ghislain Tebou
- Trotti Enrico
- Yildiz Sidar


## License

Questo progetto è distribuito sotto licenza MIT.
Vedi il file LICENSE per i dettagli.

## Argomenti per l'orale:

- ### Metodologia organizzattiva, suddivisione dei compiti e versionamento (Enrico T.)
----------
- ### Struttura del progetto in classi, blueprint (Matteo)
## Cosa é una classe?
- Una classe è un modello per l'istanza di un oggetto e questo oggetto ha le caratteristiche definite nel suo costruttore.
Es. of costruttore

```python
class Personaggio:
    def __init__(self, nome, salute, attacco, destrezza):
        self.nome = nome
        self.salute = salute
        self.attacco = attacco
        self.destrezza = destrezza
```
Es. di instanziazione

```python
personaggio1 = Personaggio("Alex", 100, 10, 15)
personaggio2 = Personaggio("Rex", 80, 8, 12)
```
Queste sono le caratteristiche dell'oggetto che verrà creato.
Ogni classe può avere i suoi metodi, ovvero delle azioni che puo eseguire l'oggetto.

Es. di un metodo

```python
class Personaggio:
    def attacca(self):
        print(f"{self.nome} attacca!")
    def subi
```
Ora quando verrà richiamato il metodo attacca, verrà stampato il nome del personaggi che sta abbaiando.


Es. di richiamo del metodo

```python
personaggio1.attacca() # Alex attacca!
personaggio2.attacca() # Rex attacca!
```
Seppur dovessimo avere diversi tipi di personaggi, possiamo usare lo stesso metodo per ogni personaggi e ottenere una stampa personalizzata agli attributi dei personaggi.

## Cosa é un blueprint?
Un blueprint è un oggetto che rappresenta una parte di un'applicazione web. In Flask usare blueprint permette un approccio modulare, suddividendo l'applicazione in componenti riutilizzabili e indipendenti, ognuno con le proprie route.
Quindi permette di gestire un grande progetto in maniera piú organizzata e scalabile, senza il bisogno di dipendere da altri.

Es. di un blueprint

```python
from flask import Blueprint

app_bp = Blueprint('app', __name__)

@app_bp.route('/home')
def home():
    return 'Hello, World!'
```
Questo blueprint ora che è stato creato potrà essere riutilizzato per altre applicazioni che ne avranno bisogno, evitando di riscrivere codice da 0.

## Perché gli abbiamo utilizzati per questo progetto?

Aver utilizzato i blueprint e le classi per il progetto ha permesso lo sviluppo in camere stagne di ogni singolo componente, senza il bisogno di dipendere da altri. Ciò permette di creare un grande progetto in maniera piú organizzata e con tempi ridotti.

Ogni blueprint/classe puó essere pensato come un mattoncino Lego. Ogni mattoncino ha delle sue caratteristiche (forma, colore, dimensioni) e puo essere riutilizzato per diverse costruzioni. 
Questo rende il lavoro svolto completamente riutilizzabile per futuri progetti, riducendo il carico di lavoro

-----------
- ### Standard per la documentazione, Docstring e Sphinx (Konrad)

- ### ORM SQLAlchemy, utenti, admin e privilegi

- ### Funzionamento Generale del software e storia (cronologia dello sviluppo) (Nik)

- ### Transizione a Flask, dalla console alla web application (Enrico M.)

- ### Raspberry (Sidar)







