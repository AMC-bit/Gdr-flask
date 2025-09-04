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
- Possibilità di creare missioni
- Possibilità di gestire autonomamente i turni e gli attacchi grazie a una modalità aggiuntiva di combattimento *"Manuale"*
- Possibilità di curare i propri personaggi una volta finita la battaglia
- Aggiunta di elementi di equipaggiamento dei personaggi (armature, armi)
- Sistema di recupero dei crediti in base al punteggio ottenuto (+ bonus in caso di vittoria)
- Multiplayer mode
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

- ### Funzionamento Generale del software e storia (cronologia dello sviluppo) (Nicolò)

- ### Struttura del progetto in classi, blueprint (Matteo)

- ### ORM SQLAlchemy, utenti, admin e privilegi (Fabrice)

- ### Transizione a Flask, dalla console alla web application (Enrico M.)

- ### Standard per la documentazione, Docstring e Sphinx (Konrad)

- ### Raspberry (Sidar)







