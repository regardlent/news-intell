# news-intell 🤖

**Analyse intelligente de l'actualité par des agents IA (LocalAI).**

`news-intell` est un projet en français qui automatise la collecte et l'analyse
de news en orchestrant plusieurs **agents IA** portés par un serveur
[**LocalAI**](https://localai.io) (conteneur Docker) exposant une API
compatible OpenAI.

---

## 🧭 Sommaire

- [Objectif](#objectif)
- [Fonctionnement](#fonctionnement)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Agents IA](#agents-ia)
- [Structure du projet](#structure-du-projet)
- [Exemples de sorties](#exemples-de-sorties)
- [Publication de releases](#publication-de-releases)
- [Contribuer](#contribuer)
- [Licence](#licence)

---

## 🎯 Objectif

Récupérer automatiquement les dernières nouvelles depuis des flux RSS de
sources francophones, puis faire analyser chaque article par une **chaîne
d'agents IA** qui produisent :

- un **résumé** synthétique ;
- une **thématique** principale et des **catégories** ;
- un **sentiment** (positif / neutre / négatif) avec un score ;
- les **entités** nommées (personnes, organisations, lieux) et **mots-clés** ;
- une note de **pertinence**.

Le tout est agrégé dans un **rapport** (Markdown, CSV ou HTML) et stocké en JSON.

## ⚙️ Fonctionnement

1. **Collecte** : récupération des articles depuis les sources RSS configurées.
2. **Analyse** : le coordinateur exécute séquentiellement les agents spécialisés.
3. **Enrichissement** : chaque agent interroge un modèle LocalAI.
4. **Stockage** : écriture des résultats dans `data/resultats.json`.
5. **Rapport** : génération d'un rapport trié par pertinence.

> Tous les prompts sont **en français**, toutes les sorties (résumés, thèmes,
> sentiments, entités) sont produites **en français**.

## 🔧 Prérequis

- **Python 3.10+** installé.
- **LocalAI** démarré dans Docker ;
  par exemple :

  ```bash
  docker run -d --name local-ai -p 8080:8080 localai/localai:latest
  ```

- Des **modèles chargés** sur votre serveur LocalAI (ex. `qwen3-4b`,
  `granite-4.2-3b-flash`, `qwen3-1.7b`, `hal-qwen3-embedding-0.6b`).

## 📦 Installation

```bash
git clone https://github.com/regardlent/news-intell.git
cd news-intell

# Créer un environnement virtuel (recommandé)
python -m venv .venv
# Windows :
.venv\Scripts\activate
# Linux / macOS :
source .venv/bin/activate

pip install -r requirements.txt

# Ou installez le projet en mode édition (fournit la commande « news-intell »)
pip install -e .
```

## ⚙️ Configuration

Copiez le fichier d'environnement et adaptez si nécessaire :

```bash
cp .env.example .env
```

Les réglages principaux se trouvent dans [`config/config.yaml`](config/config.yaml) :

- `base_url` : URL de votre serveur LocalAI (par défaut `http://localhost:8080`) ;
- `agents` : modèle + température par agent ;
- `sources` : liste des flux RSS à analyser ;
- `seuils` : seuils de sélection/pondération.

> ⏱️ La génération sur des modèles locaux peut être lente ; ajustez `timeout`
> (en secondes) dans `config/config.yaml` si nécessaire.

## 🚀 Utilisation

Depuis la racine du projet :

```bash
# Lister les modèles disponibles sur LocalAI
python -m news_intell.cli lister-modeles

# Récupérer les articles des sources
python -m news_intell.cli recuperer

# Analyser les articles récupérés (génère data/resultats.json + rapport)
python -m news_intell.cli analyser --format md

# Ou tout en une seule commande (collecte + analyse + rapport)
python -m news_intell.cli executer --format html

# Lancer le serveur web (interface journalistique + administration)
python -m news_intell.cli serveur --hote 127.0.0.1 --port 8000
# Puis ouvrir http://127.0.0.1:8000 dans votre navigateur
```

Formats de rapport disponibles : `md` (défaut), `csv`, `html`.

> 💡 Si le projet est installé en mode édition (`pip install -e .`), la
> commande équivalente est disponible directement :
>
> ```bash
> news-intell executer --format md
> news-intell lister-modeles
> ```

## 🤖 Agents IA

| Agent          | Rôle                                                        | Modèle par défaut          |
|----------------|-------------------------------------------------------------|----------------------------|
| `resume`       | Résumé synthétique de l'article (2-4 phrases)               | `qwen3-4b`                 |
| `classification` | Thématique principale + catégories                        | `granite-4.2-3b-flash`     |
| `sentiment`    | Ton (positif, neutre, négatif) + score                       | `granite-4.2-3b-flash`     |
| `entites`      | Personnes, organisations, lieux, mots-clés                   | `qwen3-1.7b`               |
| `pertinence`   | Note d'importance (0..1)                                     | `granite-4.2-3b-flash`     |

Chaque agent est une classe spécialisée de `news_intell/agents/`, orchestrée par le
[`CoordinateurAgents`](news_intell/agents/coordinator.py). Leur logique est codée en
français dans `news_intell/agents/*.py`.

Le projet intègre aussi un **cœur** d'analyse comportementale :

- **Équipe PNL** (`news_intell/agents/pnl/`) : deux agents — PNL « neuro »
  (techniques d'influence constructives) et PNL « noir » (détection des
  manipulations / dark patterns) — produisant une lecture comportementale.
- **Analyste** (`news_intell/core/analyst.py`) : rédige la **note d'analyse**
  (par écrit, en français) qui synthétise l'article, son traitement éditorial
  et sa lecture comportementale.
- **Travailleurs** (`news_intell/core/workers.py`) : enchaînent par article
  l'analyse de base, la PNL et la rédaction de la note.

Les agents agissent comme des **experts cultivés** (prompts enrichis, cadrage
rigoureux et nuancé). Le **moteur de modèle** est **pluggable**
(`news_intell/llm.py`) : serveur **LocalAI** (`backend: "localai"`) ou
**modèle local personnalisé** chargé en mémoire (`backend: "personnalise"` +
`modele_personnalise.chemin`), sans dépendre de l'API LocalAI.

Un **pipeline d'entraînement** (`scripts/entrainer_modele.py`) permet de
« cultiver » votre propre modèle sur vos données ; voir [`docs/modele.md`](docs/modele.md).

L'**analyse sémantique** complète le tout :

- **Déduplication** (`news_intell/semantic.py`) : supprime les articles quasi
  identiques (un même sujet relayé par plusieurs sources) grâce aux embeddings
  LocalAI.
- **Regroupement** : assigne un `groupe` (sujet) à chaque article et produit une
  synthèse par sujet dans le rapport.

Activez/désactivez ces étapes via `dedupe` et `clustering` dans
`config/config.yaml`.

## 🗂️ Structure du projet

```
news-intell/
├── config/
│   ├── config.yaml          # Configuration principale (sources, modèles, seuils)
│   └── prompts/             # Documentation des prompts d'agents
├── docs/
│   └── ARCHITECTURE.md      # Architecture détaillée
├── scripts/                 # Scripts de lancement (Windows / Unix)
├── news_intell/
│   ├── cli.py               # Interface en ligne de commande
│   ├── config.py            # Chargement de la configuration
│   ├── client.py            # Client HTTP vers LocalAI
│   ├── models.py            # Modèles de données (Article, AnalyseArticle)
│   ├── pipeline.py          # Pipeline haut niveau
│   ├── semantic.py          # Déduplication + regroupement sémantique
│   ├── storage.py           # Persistance JSON
│   ├── output.py            # Génération des rapports (md/csv/html)
│   ├── sources/rss.py       # Collecte des flux RSS/Atom
│   ├── agents/              # Agents IA + coordinateur
│   ├── agents/pnl/          # Agents PNL (neuro / noir)
│   ├── core/                # Analyste + travailleurs
│   └── web/                 # Interface web (FastAPI) + administration
├── tests/                   # Tests unitaires
├── .github/
│   ├── ISSUE_TEMPLATE/      # Modèles d'issues (bug, fonctionnalité)
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── dependabot.yml
│   └── workflows/           # ci.yml (tests + qualité), publish.yml (release)
├── CONTRIBUTING.md          # Guide de contribution
├── CODE_OF_CONDUCT.md       # Code de conduite
├── SECURITY.md              # Politique de sécurité
├── CHANGELOG.md             # Journal des modifications
├── ROADMAP.md               # Feuille de route
├── pyproject.toml           # Empaquetage Python + commande « news-intell »
├── requirements.txt
├── .editorconfig            # Règles d'édition partagées
├── .env.example             # Exemple de variables d'environnement
└── README.md
```

## 📊 Exemples de sorties

Un rapport Markdown ressemble à :

```markdown
# Rapport d'analyse de l'actualité

## Un grand titre de l'actualité
- **Source** : Le Monde
- **Thématique** : Politique
- **Catégories** : Économie, Europe
- **Sentiment** : neutre (0.00)
- **Pertinence** : 0.83

**Résumé** : ...
```

## 🧪 Tests

```bash
python -m unittest discover -s tests
```

## 🌐 Interface web

Le serveur web (FastAPI) propose deux volets, **en français** :

- **Public (journaliste)** : accueil, recherche, fiche article (thème, sentiment,
  entités, lecture comportementale PNL, note d'analyse).
- **Administration** (`/admin`) : statistiques, lancement d'une analyse en
  arrière-plan, édition de la configuration (`/admin/config`).

```bash
python -m news_intell.cli serveur --port 8000
```

> Le panneau admin permet de déclencher une analyse et de modifier la
> configuration (`config/config.yaml`) directement depuis le navigateur.

Un **site vitrine** de présentation/vente est fourni dans `site_vitrine/`
(landing page statique). Voir `docs/equipe_dev.md` pour l'équipe de développement.
Il peut être publié sur **GitHub Pages** (`.github/workflows/vitrine.yml`).

Pour générer **rapidement** un petit jeu d'articles analysés (sans lancer
l'analyse complète) :
```bash
python scripts/generer_exemple.py    # analyse ~2 articles (modèles rapides)
```

La **recherche** propose un mode **sémantique** (reranker LocalAI avec repli sur
les embeddings). Une **API JSON** est aussi disponible :
`/api/articles`, `/api/recherche`, `/api/article/{cle}`.

Le panneau d'administration propose en outre : **statistiques** (sources, thèmes,
sentiments, mots-clés), **export CSV** (`/api/export.csv`) et **planification
périodique** des analyses (`/admin/planifier`).

## 📦 Publication de releases

Lancez une publication en créant un tag versionné à partir de `main` :

```bash
git tag v0.1.0
git push origin v0.1.0
```

Le workflow [`.github/workflows/publish.yml`](.github/workflows/publish.yml) exécute
les tests, construit le paquet et crée une **release GitHub** avec le paquet
(`.whl` + `.tar.gz`) en pièce jointe.

## 🤝 Contribuer

Merci de vouloir contribuer ! Vous trouverez ci-dessous les principaux points
d'entrée du projet :

- [Guide de contribution](CONTRIBUTING.md) — comment proposer un changement.
- [Code de conduite](CODE_OF_CONDUCT.md) — les règles de la communauté.
- [Politique de sécurité](SECURITY.md) — signaler une vulnérabilité.
- [Journal des modifications](CHANGELOG.md) — l'historique des évolutions.
- [Feuille de route](ROADMAP.md) — la vision et les prochaines étapes.

Deux types de demandes sont possibles via les modèles fournis :

- 🐛 Rapporter un **bug** ([template](.github/ISSUE_TEMPLATE/bug_report.yml))
- 💡 Proposer une **fonctionnalité** ([template](.github/ISSUE_TEMPLATE/feature_request.yml))

À chaque ouverture de **pull request**, utilisez le
[modèle de pull request](.github/PULL_REQUEST_TEMPLATE.md).

## 📄 Licence

Ce projet est distribué sous la licence
[Apache License 2.0](LICENSE).
