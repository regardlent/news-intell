# Architecture du projet news-intell

## Vue d'ensemble

`news-intell` est une application en Python qui collecte des news depuis des
flux RSS/Atom, puis les analyse avec une chaîne d'**agents IA** s'appuyant sur
un serveur **LocalAI** (API compatible OpenAI).

```
                    ┌───────────────────────────────────────────┐
                    │                  CLI (news_intell/cli.py)         │
                    └───────────────┬───────────────────────────┘
                                    │
                    ┌───────────────▼───────────────────────────┐
                    │              Pipeline (news_intell/pipeline.py)   │
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

1. **Sources (`news_intell/sources/rss.py`)** : téléchargement et analyse de flux
   RSS/Atom à l'aide de `requests` et de `xml.etree.ElementTree`. Produit des
   objets `Article`.

2. **Client (`news_intell/client.py`)** : client HTTP minimaliste vers l'API
   OpenAI-compatible de LocalAI (`/v1/chat/completions`, `/v1/embeddings`,
   `/v1/models`), avec plafonnement de `max_tokens`.

3. **Agents (`news_intell/agents/`)** : chaque agent est une classe héritant de
   `Agent`, avec une mission propre (`resume`, `classification`, `sentiment`,
   `entites`, `pertinence`). Ils construisent des prompts **en français** et
   parseent une réponse JSON.

4. **Coordinateur (`news_intell/agents/coordinator.py`)** : exécute les agents en
   séquence sur un article et agrège le résultat dans `AnalyseArticle`.

5. **Équipe PNL (`news_intell/agents/pnl/`)** : analyse comportementale du discours.
   Deux agents spécialisés — PNL « neuro » (communication constructive) et PNL
   « noir » (détection des manipulations / dark patterns) — agrégés par
   `EquipePNL` en une `AnalysePNL` (score de manipulation, boutons chauds…).

6. **Cœur (`news_intell/core/`)** : l'**Analyste** rédige la note d'analyse
   comportementale (par écrit, en français) ; les **Travailleurs**
   (`Travailleur`, `ParcTravailleurs`) enchaînent par article : analyse de base →
   PNL → rédaction de la note.

7. **Pipeline (`news_intell/pipeline.py`)** : enchaîne la récupération, l'analyse
   (via `ParcTravailleurs`) et la production des fichiers de sortie.

8. **Persistance (`news_intell/storage.py`)** : lecture/écriture JSON
   (`data/articles.json`, `data/resultats.json`).

9. **Rapports (`news_intell/output.py`)** : conversion des analyses (y compris la
   lecture PNL et la note) vers des rapports Markdown, CSV ou HTML.

> Le pipeline applique aussi l'**analyse sémantique** (`news_intell/semantic.py`) :
> déduplication (suppression des doublons) et regroupement (assignation d'un
> `groupe`) à l'aide des embeddings de LocalAI (`hal-qwen3-embedding-0.6b`).

> L'**interface web** est servie par FastAPI (`news_intell/web/app.py`) avec des
> vues Jinja2 ; elle expose un volet public (journaliste) et un volet
> d'administration (configuration, lancement d'analyses).

## Flux de données

```
Flux RSS ──► list[Article]
                 │
                 ▼
      ParcTravailleurs.traiter_lot(articles)
                 │  (pour chaque article : CoordinateurAgents → EquipePNL → Analyste)
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
- Les agents PNL sont isolés : une erreur est enregistrée dans `AnalysePNL.erreurs`
  sans bloquer l'analyse ; de même pour l'analyste (`AnalyseArticle.erreurs`).

## Extension possible

- Ajouter un agent en créant une nouvelle classe héritant de `Agent` et en
  l'ajoutant à la liste du `CoordinateurAgents`.
- Externaliser les prompts dans `config/prompts/`.
- Utiliser l'embedding et le reranker (`jina-reranker-v1-base-en`) pour
  rapprocher des articles similaires ou dédupliquer par similarité sémantique.
- Ajouter de nouvelles sources (API, scraping, alertes) dans `sources/`.
