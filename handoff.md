# Handoff per Claude Code

Aggiornato: 2026-06-11

## Obiettivo del progetto

Questa repository contiene il portfolio personale di un hardware designer.
Il sito deve essere pubblicato tramite GitHub Pages e Jekyll.

L'obiettivo estetico dichiarato e' uno stile classico, simile ai primi siti HTML statici:

- plain and simple;
- nessuna transizione;
- nessuna ombra;
- nessuna grafica moderna;
- niente componenti in stile landing page;
- contenuto tecnico leggibile e diretto.

Il sito deve presentare progetti hardware, schede, prototipi, note di progettazione, layout PCB, test e risultati.

## Stato attuale

E' stata creata una fondazione Jekyll minimale e gia' pushata su GitHub.

Repository remota:

```text
https://github.com/steveqhw/personal-portfolio.git
```

Branch usato:

```text
main
```

Commit principale gia' pushato:

```text
115e6a1 Create Jekyll portfolio foundation
```

Nota: dopo la creazione di questo handoff, ci sara' almeno una modifica locale non ancora inclusa nel commit precedente, cioe' questo file `handoff.md`.

## Struttura del sito

File principali creati:

```text
_config.yml
Gemfile
.gitignore
README.md
index.md
projects.md
about.md
contact.md
_includes/header.html
_includes/footer.html
_layouts/default.html
_layouts/project.html
_projects/progetto-di-esempio.md
assets/css/style.css
```

## Configurazione Jekyll

Il sito usa Jekyll senza tema esterno.

In `_config.yml` sono impostati:

- titolo: `Portfolio Hardware`;
- descrizione: `Portfolio personale di progetti hardware`;
- collection `projects`;
- permalink puliti;
- layout predefinito `project` per i file nella collection `_projects`.

La configurazione attuale usa:

```yml
baseurl: "/personal-portfolio"
```

Questa scelta e' corretta per una GitHub project page pubblicata sotto:

```text
https://<username>.github.io/personal-portfolio/
```

Se il sito verra' pubblicato con dominio personalizzato oppure come repository `username.github.io`, cambiare in:

```yml
baseurl: ""
```

## Pagine esistenti

### `index.md`

Home page del portfolio.
Contiene una breve introduzione e mostra fino a 3 progetti dalla collection `site.projects`.

### `projects.md`

Archivio dei progetti.
Itera su `site.projects` e linka le pagine dei singoli progetti.

### `about.md`

Pagina profilo.
Contiene testo segnaposto su competenze e metodo.

### `contact.md`

Pagina contatti.
Contiene placeholder per email, GitHub e LinkedIn.

### `_projects/progetto-di-esempio.md`

Template iniziale per un progetto hardware.
Le sezioni presenti sono:

- Sintesi;
- Obiettivo;
- Architettura;
- Scelte progettuali;
- PCB;
- Test;
- File e riferimenti.

Questo file va considerato un modello da sostituire o duplicare per i progetti reali.

## Layout e include

### `_layouts/default.html`

Layout HTML principale.
Include:

- `head` minimale;
- meta viewport;
- titolo pagina;
- CSS custom;
- header;
- contenuto;
- footer.

### `_layouts/project.html`

Layout dedicato ai progetti.
Mostra una tabella con metadata del progetto:

- anno;
- categoria;
- stato.

Poi renderizza il contenuto Markdown del progetto.

### `_includes/header.html`

Header comune con:

- titolo sito;
- descrizione;
- navigazione principale;
- separatore orizzontale.

### `_includes/footer.html`

Footer comune con copyright e data di aggiornamento generata da Jekyll.

## Stile CSS

File:

```text
assets/css/style.css
```

Scelte attuali:

- font serif classico: Georgia / Times;
- sfondo bianco;
- testo nero;
- link blu e viola visitato, stile web classico;
- larghezza contenuto massima di circa 900px;
- tabelle con bordi neri semplici;
- nessuna ombra;
- nessuna animazione;
- nessuna transizione;
- nessun framework CSS;
- responsive minimo per mobile.

Mantenere questo registro visivo anche nelle prossime modifiche.

## Istruzioni per aggiungere progetti

Creare un nuovo file Markdown in `_projects/`.

Esempio:

```md
---
title: "Nome progetto"
year: "2026"
category: "PCB design"
status: "Completato"
summary: "Breve descrizione del progetto."
---

## Sintesi

Descrizione sintetica del progetto.

## Obiettivo

Problema tecnico o funzionale affrontato.

## Architettura

Blocchi principali del sistema.

## Scelte progettuali

Decisioni tecniche rilevanti.

## PCB

Note su layout, vincoli e routing.

## Test

Misure, strumenti e risultati.
```

## Verifiche gia' fatte

E' stato eseguito:

```text
git diff --check
```

Risultato: nessun errore di whitespace.

Non e' stato possibile eseguire localmente:

```text
bundle exec jekyll build
```

Motivo: nella shell usata in precedenza non erano disponibili `ruby` e `bundle`.

Prima di pubblicare modifiche future importanti, installare Ruby/Bundler oppure usare il build di GitHub Pages come verifica remota.

## Prossimi passi consigliati

1. Sostituire i placeholder personali.

   Aggiornare:

   - `site.author` in `_config.yml`;
   - testo della home;
   - `about.md`;
   - `contact.md`;
   - link GitHub/LinkedIn/email.

2. Decidere la struttura dei contenuti dei progetti.

   Ogni progetto hardware dovrebbe avere almeno:

   - contesto;
   - obiettivo;
   - architettura;
   - schema a blocchi, se disponibile;
   - componenti principali;
   - note sullo schema elettrico;
   - note sul PCB;
   - bring-up;
   - test;
   - risultati;
   - immagini o file pubblicabili.

3. Aggiungere asset statici.

   Creare, se necessario:

   ```text
   assets/images/
   assets/files/
   ```

   Usarli per immagini di PCB, render, foto banco prova, diagrammi, PDF o datasheet pubblicabili.

4. Migliorare la navigazione mantenendo lo stile classico.

   Possibili aggiunte:

   - pagina `notes.md` per note tecniche;
   - pagina `tools.md` per strumenti usati;
   - indice per anno o categoria;
   - tabella progetti invece della lista, se il numero cresce.

5. Validare GitHub Pages.

   Controllare nelle impostazioni della repository:

   - Pages abilitato;
   - branch `main`;
   - sorgente corretta;
   - URL generato;
   - coerenza del `baseurl`.

## Vincoli da rispettare

- Non introdurre framework frontend.
- Non aggiungere animazioni o transizioni.
- Non usare layout moderni tipo hero, card, gradienti o sezioni marketing.
- Non usare shadow, blur, glassmorphism o componenti decorativi.
- Preferire HTML semantico e Markdown semplice.
- Mantenere il sito facile da leggere anche senza JavaScript.
- Usare JavaScript solo se davvero necessario; al momento non serve.
- Trattare il portfolio come documentazione tecnica pubblica, non come landing page.

## Nota operativa per Claude Code

Partire da questo handoff e leggere questi file prima di modificare:

```text
_config.yml
_layouts/default.html
_layouts/project.html
assets/css/style.css
index.md
projects.md
_projects/progetto-di-esempio.md
README.md
```

Prima di fare commit o push:

```text
git status -sb
git diff --check
```

Se Ruby e Bundler sono disponibili:

```text
bundle install
bundle exec jekyll build
```

Se il build non e' disponibile localmente, indicare chiaramente che la verifica Jekyll non e' stata eseguita.
