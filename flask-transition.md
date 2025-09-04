# Transizione a Flask: dalla console all'applicazione web.

A un certo punto, durante lo sviluppo del progetto, a causa dell'aumentare della complessità dello stesso, è stato necessario dare un'interfaccia grafica al software.

> Invece di scrivere (*input*) e leggere (*output*) nel terminale, adesso scriviamo gli input e leggiamo gli output della nostra applicazione all'interno di pagine web (*templates*).

Come far comunicare questi *template* con la nostra applicazione?

## Flask: cos'è Flask?

**Flask** è un framework (letteralmente un'*impalcatura* che facilita il lavoro) Python che ci aiuta a gestire le interazioni tra l'applicazione e le pagine web, creando, per l'appunto, un'**applicazione web**.

## Come abbiamo effettuato la transizione a Flask:

- Abbiamo isolato la logica del programma dal resto, eliminando tutte le richieste di input e gli output in terminale.

Con un'**interfaccia web**, cambiano alcune cose:

- **Input:** vengono sostituiti con form e pulsanti. Questo sarà per l'utente il modo di comunicare con il software. Quando l'utente preme un pulsante, il browser (Es. Google Chrome, Firefox...) manda i dati al programma, che li elabora e restituisce un risultato.
- **Output:** il risultato di queste elaborazioni viene inviato a schermo su pagine web interattive.

- Una volta ottenuta un'applicazione web funzionante, abbiamo curato, anche se essenzialmente, il layout e lo stile delle pagine web.

## I vantaggi della transizione

- **Accessibilità:** Chiunque può utilizzare l'applicazione da browser. L'interfaccia web permette di inserire dati, cliccando pulsanti invece di scrivere comandi in console.
- **Flessibilità:** Una volta portato il programma su web, diventa molto più facile l'aggiunta e il testing di nuove funzionalità

