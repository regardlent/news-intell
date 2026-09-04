# Architecture du projet news-intell

## Vue d'ensemble

`news-intell` est une application en Python qui collecte des news depuis des
flux RSS/Atom, puis les analyse avec une chaîne d'**agents IA** s'appuyant sur
un serveur **LocalAI** (API compatible OpenAI).

```
                    ┌───────────────────────────────────────────┐
                    │                  CLI (src/cli.py)         │
                    └───────────────┬───────────────────────────┘
                                    │
                    ┌───────────────▼───────────────────────────┐
                    │              Pipeline (src/pipeline.py)   │
                    │  recuperer ──► analyser ──► stockage ──► rapport │
                    └───────┬────────────────┬─────────────┬─────┘
                            │                │             │
              ┌─────────────▼────┐   ┌───────▼────────┐   ┌▼──────────────────┐
              │  sources/rss.py  │   │ agents/coordinateur.py │  output.py (md/csv/html) │
              │  (flux RSS/Atom) │   │  (multi-agents) │   │  storage.py (JSON)│
              └─────────┬───────┘   └───────┬────────┘   └────────────────────┘
                        │                   │
                        │   ┌───────────────▼───────────────┐
                        └──►│        client.py (LocalAI)    │
                            │  /v1/chat/completions         │
                            │  /v1/embeddings               │
                            └───────────────┬───────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │  LocalAI (conteneur Docker)│
                              │  port 8080                │
                              └───────────────────────────┘
```

## Couches applicatives

1. **Sources (`src/sources/rss.py`)** : téléchargement et analyse de flux
   RSS/Atom à l'aide de `requests` et de `xml.etree.ElementTree`. Produit des
   objets `Article`.

2. **Client (`src/client.py`)** : client HTTP minimaliste vers l'API
   OpenAI-compatible de LocalAI (`/v1/chat/completions`, `/v1/embeddings`,
   `/v1/models`).

3. **Agents (`src/agents/`)** : chaque agent est une classe héritant de
   `Agent`, avec une mission propre (`resume`, `classification`, `sentiment`,
   `entites`, `pertinence`). Ils construisent des prompts **en français** et
   parseent une réponse JSON.

4. **Coordinateur (`src/agents/coordinator.py`)** : exécute les agents en
   séquence sur un article et agrège le résultat dans `AnalyseArticle`.

5. **Pipeline (`src/pipeline.py`)** : enchaîne la récupération, l'analyse et la
   production des fichiers de sortie.

6. **Persistance (`src/storage.py`)** : lecture/écriture JSON
   (`data/articles.json`, `data/resultats.json`).

7. **Rapports (`src/output.py`)** : conversion des analyses vers des rapports
   Markdown, CSV ou HTML.

## Flux de données

```
Flux RSS ──► list[Article]
                 │
                 ▼
      CoordinateurAgents.analyser_lot(articles)
                 │  (pour chaque article, exécute les agents)
                 ▼
           list[AnalyseArticle]
                 │
                 ▼
   storage.sauvegarder_resultats  ──►  data/resultats.json
                 │
                 ▼
        output.generer_rapport  ──►  data/rapport.md|.csv|.html
```

## Robustesse

- Chaque agent est isolé : une erreur d'un agent est enregistrée dans
  `AnalyseArticle.erreurs` sans interrompre le reste de la chaîne.
- La collecte RSS tolère les flux indisponibles (retourne une liste vide).
- La réponse JSON d'un agent est parseée de façon tolérante (`Agent.extraire_json`).

## Extension possible

- Ajouter un agent en créant une nouvelle classe héritant de `Agent` et en
  l'ajoutant à la liste du `CoordinateurAgents`.
- Externaliser les prompts dans `config/prompts/`.
- Utiliser l'embedding et le reranker (`jina-reranker-v1-base-en`) pour
  rapprocher des articles similaires ou dédupliquer par similarité sémantique.
- Ajouter de nouvelles sources (API, scraping, alertes) dans `sources/`.
