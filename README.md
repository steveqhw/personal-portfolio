# Stefano Quagliarella — hardware portfolio

Portfolio tecnico bilingue, generato con Jekyll e pubblicato come GitHub Pages project site. Il sito è rivolto principalmente a recruiter e hiring manager che valutano competenze in hardware elettronico embedded.

## Caratteristiche

- Home equivalente in inglese (`/`) e italiano (`/it/`).
- Tre dossier tecnici, ciascuno con route EN/IT e cambio lingua puntuale.
- Profilo, competenze, percorso professionale e fase accademica in un'unica struttura dati.
- Modulo Formspree utilizzabile senza JavaScript.
- Informativa privacy bilingue, metadati localizzati, canonical e `hreflang`.
- CSS custom con font di sistema; nessun framework, font remoto, analytics o runtime frontend.
- Contenuto e navigazione principali utilizzabili senza JavaScript.

## Contenuti modificabili

I contenuti pubblici sono centralizzati in `_data/`:

| File | Contenuto |
|---|---|
| `_data/site.yml` | Profilo pubblico, social, Formspree, disponibilità e route privacy |
| `_data/ui.yml` | Copy e label equivalenti EN/IT |
| `_data/projects.yml` | Schede riepilogo, route, SEO e dossier dei progetti |
| `_data/experience.yml` | Esperienza professionale e fase accademica |
| `_data/services.yml` | Competenze lungo il ciclo di vita della scheda |
| `_data/toolbox.yml` | Ambiti tecnici e strumenti |

Per un nuovo progetto occorrono un record bilingue completo e due entry point sotto `work/` e `it/work/`. Gli ID devono essere univoci; percorsi, array del dossier e metadati devono avere la rispettiva controparte linguistica. Non pubblicare dati del CV privato, nomi dei datori di lavoro, contatti diretti, schematici o risultati non autorizzati.

Le immagini pubbliche risiedono in `assets/images/`. Specificare un testo alternativo EN/IT; quando un'immagine non è disponibile, il template mostra una dichiarazione testuale invece di un mockup.

## Architettura

```text
_data/*.yml                    contenuti verificati e localizzati
index.html, it/index.html      home EN/IT
work/**, it/work/**            sei entry point dei dossier
privacy/**, it/privacy/**      informativa EN/IT
_layouts/default.html         shell condivisa e metadati
_layouts/project.html         rendering guidato da project_id
_includes/                    navigazione, footer e sezioni home
assets/css/style.css           design system responsive
404.html                      recupero bilingue
robots.txt, sitemap.xml        discovery per crawler
```

Tutti gli URL locali nei template devono attraversare `relative_url` o `absolute_url`, perché il deploy corrente usa `baseurl: /personal-portfolio`.

## Modulo di contatto

L'endpoint pubblico è configurato come `formspree_id` in `_data/site.yml`. Il contratto dei campi è:

- `name`, `email`, `message` obbligatori;
- `_language` nascosto;
- `_gotcha` come honeypot.

Non rinominare questi campi senza coordinare la configurazione Formspree. Le informative sono disponibili a `/privacy/` e `/it/privacy/`.

## Esecuzione locale

Richiede Ruby e Bundler:

```sh
bundle install
bundle exec jekyll serve
```

Build di verifica:

```sh
bundle exec jekyll build
git diff --check
```

## Pubblicazione e dominio

Configurazione corrente:

```yml
url: "https://steveqhw.github.io"
baseurl: "/personal-portfolio"
```

Per un futuro dominio `steveqhw.com`, impostare `url` al dominio, svuotare `baseurl`, aggiungere il `CNAME` e completare la configurazione DNS/GitHub Pages. Contenuti e route non richiedono una nuova architettura.

`.agents/`, il CV privato, la documentazione di handoff e gli output di build sono esclusi dal sito pubblico.
