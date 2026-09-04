# Journal des modifications

Tous les changements notables de **news-intell** sont documentés dans ce
fichier, en français. Le format suit les principes
de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

## [Non publié]

### Ajouts

- Empaquetage Python : `pyproject.toml` avec la commande `news-intell`.
- Ajout de **Ruff** pour la vérification du style de code (étape de CI).
- Workflow de publication de releases GitHub (`.github/workflows/publish.yml`).
- Fichier `.editorconfig` pour des règles d'édition cohérentes.
- Ajout du **cœur** du projet : agents **PNL** (analyse comportementale « neuro »
  et « noir »), **Analyste** (note écrite) et **travailleurs** (`Travailleur`,
  `ParcTravailleurs`).
- Plafonnement de `max_tokens` pour maîtriser la durée de génération des modèles
  locaux.
- Ajout de l'**analyse sémantique** : déduplication et regroupement d'articles
  via les embeddings (`news_intell/semantic.py`).
- Ajout de l'**interface web** (FastAPI + Jinja2) : lecture journalistique,
  recherche et panneau d'administration (lancement d'analyses, configuration).
- Commande CLI `serveur` pour lancer l'interface web.
- Ajout d'une **recherche sémantique** (reranker, repli embeddings) et d'une
  **API JSON** (`/api/articles`, `/api/recherche`, `/api/article/{cle}`).
- Panneau d'**administration** enrichi : statistiques, **export CSV** et
  **planification périodique** des analyses.
- Enrichissement des **sources RSS francophones** (8 médias vérifiés : Le Monde,
  France 24, France Info, Le Figaro, RFI, Ouest-France, Sud Ouest, Marianne) et
  User-Agent navigateur pour améliorer la récupération des flux.
- Script `scripts/generer_exemple.py` pour générer rapidement un petit jeu
  d'articles analysés (alimente l'interface sans lancer l'analyse complète).
- Agents rendus plus **cultivés et experts** (prompts enrichis).
- Moteur de modèle **pluggable** : LocalAI ou **modèle local personnalisé**
  (GGUF, sans API LocalAI) via `news_intell/llm.py`.
- Ajout d'un **site vitrine** (`site_vitrine/`) et de la documentation de
  l'équipe de développement (`docs/equipe_dev.md`).
- Pipeline d'entraînement d'un **modèle local personnalisé**
  (`scripts/entrainer_modele.py`) + documentation `docs/modele.md`.
- Déploiement du **site vitrine** sur GitHub Pages
  (`.github/workflows/vitrine.yml`).
- Site vitrine enrichi : **maquettes SVG** (`site_vitrine/assets/`) et section
  **« Démo en direct »** branchée sur l'API (CORS activé sur le serveur web).

### Prévu

- Ajout d'un agent de traduction pour normaliser la langue des articles.
- Utilisation de l'embedding (`hal-qwen3-embedding-0.6b`) et du reranker
  (`jina-reranker-v1-base-en`) pour rapprocher des articles similaires.
- Recherche sémantique sur les articles analysés.
- Génération de rapports périodiques automatisés (planification).

## [0.1.0] - 2026-09-04

### Ajouts

- Projet initial **news-intell** : analyse intelligente de l'actualité par des
  agents IA basés sur **LocalAI**.
- Collecte d'articles depuis des flux RSS / Atom (plusieurs sources
  francophones configurables).
- Cinq agents spécialisés (résumé, classification, sentiment, entités,
  pertinence) orchestrés par un coordinateur.
- Pipeline complet : récupération → analyse → stockage JSON → rapport.
- Génération de rapports au format **Markdown**, **CSV** et **HTML**.
- Interface en ligne de commande (`python -m news_intell.cli`).
- Configuration centralisée (`config/config.yaml` + `.env`).
- Tests unitaires et **CI GitHub Actions**.

### Sécurité

- Les clés d'API et fichiers d'environnement sont exclus du versionnage
  (`.gitignore`).

---

*Le format de ce journal s'inspire de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).*
