---
layout: default
title: Progetti
permalink: /projects/
---

## Progetti

Archivio dei progetti hardware documentati nel portfolio.

<ul class="project-list">
{% for project in site.projects %}
  <li>
    <h3><a href="{{ project.url | relative_url }}">{{ project.title }}</a></h3>
    <p class="project-meta">{{ project.year }}{% if project.category %} - {{ project.category }}{% endif %}</p>
    {% if project.summary %}
      <p>{{ project.summary }}</p>
    {% endif %}
  </li>
{% endfor %}
</ul>

Per aggiungere un progetto, crea un nuovo file Markdown nella cartella `_projects`.
