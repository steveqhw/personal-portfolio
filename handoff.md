# Handoff tecnico — portfolio Jekyll

Aggiornato: 2026-08-05

## Stato architetturale

Il portfolio usa Jekyll nativo su GitHub Pages. L'esperienza inglese vive alla root e quella italiana sotto `/it/`. Layout e include sono condivisi; i contenuti bilingui sono in `_data/` e i dossier sono pagine leggere selezionate tramite `project_id`.

La direzione visiva autorevole è un dossier tecnico-editoriale: tipografia di sistema, regole nette, colore industriale contenuto, evidenze e limiti dichiarati. Non reintrodurre gradienti, glow, glass effect, animazioni reveal, font di rete o navigazione mobile dipendente da JavaScript.

## Contratti da preservare

- Route home: `/` e `/it/`.
- Route dossier: tre coppie dichiarate in `_data/projects.yml`.
- Route privacy: `/privacy/` e `/it/privacy/`.
- Lingua: `page.lang` uguale a `en` o `it`; ogni pagina pubblica dichiara il counterpart.
- URL: usare sempre `relative_url` o `absolute_url` per rispettare `baseurl`.
- Formspree: metodo POST; campi `name`, `email`, `message`, `_language`, `_gotcha`.
- Social: mantenere LinkedIn e GitHub da `_data/site.yml`.
- Riservatezza: nessun datore di lavoro, telefono, email privata, CV o dettaglio tecnico confidenziale nel prodotto pubblico.
- Dossier: separare contesto, fatti verificati, approccio, elementi realizzati, evidenza pubblica e limiti.

## File principali

- `_layouts/default.html`: risolve locale, metadata, canonical, alternate e shell.
- `_layouts/project.html`: trova il record tramite ID e renderizza il dossier.
- `_includes/header.html`: navigazione sempre visibile e cambio lingua puntuale.
- `_includes/sections/*.html`: home recruiter-first nell'ordine selected work, profile, capabilities, trajectory, contact.
- `assets/css/style.css`: responsive 320–1440 px, focus visibile e stampa.
- `robots.txt` e `sitemap.xml`: generati con `absolute_url`.

Non esiste uno script frontend: modulo, route, navigazione e contenuti funzionano nativamente.

## Aggiungere o modificare un dossier

1. Aggiornare il record in `_data/projects.yml` mantenendo tutti i campi EN/IT.
2. Aggiungere le due pagine con front matter sotto `work/` e `it/work/`.
3. Impostare lo stesso `project_id`, permalink, counterpart e alternate URL.
4. Aggiungere solo immagini approvate, con alt localizzati e dimensioni HTML coerenti.
5. Aggiornare `sitemap.xml` solo se la route non deriva dall'iterazione sui progetti.

## Verifiche prima del rilascio

```sh
bundle exec jekyll build
git diff --check
```

Verificare inoltre:

- parità delle chiavi e degli array EN/IT;
- unicità di ID, slug e path;
- corrispondenza dei `project_id`;
- endpoint/campi Formspree;
- canonical, hreflang e counterpart generati;
- assenza di PII, nomi dei datori di lavoro e file privati;
- navigazione da tastiera, 320/768/1440 px e zoom testo 200%;
- resa senza JavaScript e con immagini disabilitate.

## Limiti operativi

Il repository non contiene un backend, analytics o gestione locale del consenso. Formspree è un confine esterno e gestisce consegna e conservazione dei messaggi secondo la propria configurazione. Il rollback consiste nel ripristino Git di una revisione nota e in un nuovo deploy Pages.
