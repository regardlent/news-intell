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

## 🚀 Utilisation

Depuis la racine du projet :

```bash
# Lister les modèles disponibles sur LocalAI
python -m src.cli lister-modeles

# Récupérer les articles des sources
python -m src.cli recuperer

# Analyser les articles récupérés (génère data/resultats.json + rapport)
python -m src.cli analyser --format md

# Ou tout en une seule commande (collecte + analyse + rapport)
python -m src.cli executer --format html
```

Formats de rapport disponibles : `md` (défaut), `csv`, `html`.

## 🤖 Agents IA

| Agent          | Rôle                                                        | Modèle par défaut          |
|----------------|-------------------------------------------------------------|----------------------------|
| `resume`       | Résumé synthétique de l'article (2-4 phrases)               | `qwen3-4b`                 |
| `classification` | Thématique principale + catégories                        | `granite-4.2-3b-flash`     |
| `sentiment`    | Ton (positif, neutre, négatif) + score                       | `granite-4.2-3b-flash`     |
| `entites`      | Personnes, organisations, lieux, mots-clés                   | `qwen3-1.7b`               |
| `pertinence`   | Note d'importance (0..1)                                     | `granite-4.2-3b-flash`     |

Chaque agent est une classe spécialisée de `src/agents/`, orchestrée par le
[`CoordinateurAgents`](src/agents/coordinator.py). Leur logique est codée en
français dans `src/agents/*.py`.

## 🗂️ Structure du projet

```
news-intell/
├── config/
│   ├── config.yaml          # Configuration principale (sources, modèles, seuils)
│   └── prompts/             # Documentation des prompts d'agents
├── docs/
│   └── ARCHITECTURE.md      # Architecture détaillée
├── scripts/                 # Scripts de lancement (Windows / Unix)
├── src/
│   ├── cli.py               # Interface en ligne de commande
│   ├── config.py            # Chargement de la configuration
│   ├── client.py            # Client HTTP vers LocalAI
│   ├── models.py            # Modèles de données (Article, AnalyseArticle)
│   ├── pipeline.py          # Pipeline haut niveau
│   ├── storage.py           # Persistance JSON
│   ├── output.py            # Génération des rapports (md/csv/html)
│   ├── sources/rss.py       # Collecte des flux RSS/Atom
│   └── agents/              # Agents IA + coordinateur
├── tests/                   # Tests unitaires
├── requirements.txt
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

## 📄 Licence

Ce projet est distribué sous la licence
[Apache License 2.0](LICENSE).
