---
layout: default
title: Home
---

## Portfolio di progetti hardware

Questo sito raccoglie progetti, schede, prototipi e note tecniche legate al mio lavoro di hardware designer.

L'obiettivo e' documentare in modo chiaro:

- il problema affrontato;
- le scelte di architettura hardware;
- le parti principali dello schema elettrico;
- le decisioni di layout PCB;
- i test eseguiti e i risultati ottenuti.

## Progetti in evidenza

<ul class="project-list">
{% for project in site.projects limit:3 %}
  <li>
    <h3><a href="{{ project.url | relative_url }}">{{ project.title }}</a></h3>
    <p class="project-meta">{{ project.year }}{% if project.category %} - {{ project.category }}{% endif %}</p>
    {% if project.summary %}
      <p>{{ project.summary }}</p>
    {% endif %}
  </li>
{% endfor %}
</ul>

Vai alla pagina completa dei [progetti]({{ '/projects/' | relative_url }}).
