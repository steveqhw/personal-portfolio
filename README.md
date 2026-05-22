# Personal Portfolio

Repository per il portfolio personale di progetti hardware, pubblicato con GitHub Pages e Jekyll.

## Struttura

- `_config.yml`: configurazione Jekyll.
- `_layouts/`: layout HTML del sito.
- `_includes/`: parti comuni come header e footer.
- `_projects/`: pagine Markdown dei singoli progetti.
- `assets/css/style.css`: stile minimale del sito.
- `index.md`, `projects.md`, `about.md`, `contact.md`: pagine principali.

## Aggiungere un progetto

Crea un file Markdown in `_projects/`, per esempio:

```md
---
title: "Nome progetto"
year: "2026"
category: "PCB design"
status: "Completato"
summary: "Breve descrizione del progetto."
---

## Sintesi

Testo del progetto.
```

## Esecuzione locale

Se Ruby e Bundler sono installati:

```sh
bundle install
```

Poi avvia il sito:

```sh
bundle exec jekyll serve
```

In alternativa GitHub Pages generera' il sito automaticamente dal branch configurato nelle impostazioni della repository.

Nota: `_config.yml` usa `baseurl: "/personal-portfolio"`, adatto a una GitHub project page pubblicata sotto `https://<username>.github.io/personal-portfolio/`. Se userai un dominio personalizzato o una repository `username.github.io`, imposta `baseurl: ""`.
