# Stefano Quagliarella — Portfolio

Sito bilingue (IT/EN) costruito con Jekyll e pubblicato su GitHub Pages.
Stile dark/tech, pensato come vetrina freelance e CV professionale.

## Come modificare i contenuti (senza toccare il codice)

Quasi tutto si modifica dai file in **`_data/`**:

| File | Cosa contiene |
|------|---------------|
| `_data/site.yml` | LinkedIn, GitHub, **ID Formspree**, località |
| `_data/ui.yml` | Tutti i testi dell'interfaccia, in **IT e EN** (hero, titoli sezioni, bottoni) |
| `_data/services.yml` | I servizi offerti (IT/EN) |
| `_data/experience.yml` | Esperienze lavorative (descrizioni generiche, no NDA) |
| `_data/projects.yml` | Progetti personali/freelance + nome delle foto |
| `_data/toolbox.yml` | Competenze/strumenti mostrati come "chip" |

### 1. Form di contatto
Già attivo via Formspree (`formspree_id` in `_data/site.yml`).
Le email arrivano all'indirizzo configurato nell'account Formspree.

### 2. Aggiungere le foto dei progetti
1. Carica le immagini in `assets/images/` (jpg/webp, lato lungo ~1600px).
2. In `_data/projects.yml`, scrivi il nome file nel campo `image:` del progetto.
   Se lasci `image: ""` viene mostrato un placeholder grafico.

⚠️ Il CV completo in `_data/*.md` è in `.gitignore` e **non** viene pubblicato.

## Struttura

```
_config.yml              configurazione e baseurl
_data/                   contenuti modificabili (vedi sopra)
_layouts/default.html    layout base (head + header + footer + JS)
_includes/               head, header (con switch lingua), footer
_includes/sections/      hero, about, services, experience, projects, contact
index.html               home in inglese        ( / )
it/index.html            home in italiano        ( /it/ )
assets/css/style.css     stile dark/tech
assets/js/main.js        menu mobile, reveal, header sticky
assets/images/           foto progetti
```

## Pubblicazione

Attualmente: GitHub Pages project page → `https://steveqhw.github.io/personal-portfolio/`
con `baseurl: "/personal-portfolio"` in `_config.yml`.

### Passare al dominio steveqhw.com
1. In `_config.yml` imposta `url: "https://steveqhw.com"` e `baseurl: ""`.
2. Crea un file `CNAME` nella root con dentro `steveqhw.com`.
3. Su GoDaddy punta il DNS a GitHub Pages e abilita il dominio in *Settings → Pages*.

## Esecuzione locale (opzionale)

Richiede Ruby + Bundler:

```sh
bundle install
bundle exec jekyll serve
```

Senza Ruby, il build di GitHub Pages funge da verifica remota.
