# Contribution au projet news-intell

Merci de votre intérêt pour **news-intell** ! 🎉 Ce guide vous aide à
contribuer efficacement. Les échanges, les issues et les pull requests se font
**en français**.

## 🧭 Table des matières

- [Prérequis](#prérequis)
- [Créer une issue](#créer-une-issue)
- [Travailler sur une branche](#travailler-sur-une-branche)
- [Conventions de commit](#conventions-de-commit)
- [Tests](#tests)
- [Style de code](#style-de-code)
- [Ouvrir une pull request](#ouvrir-une-pull-request)

## 🔧 Prérequis

1. **Python 3.10+** installé.
2. Le dépôt cloné :
   ```bash
   git clone https://github.com/regardlent/news-intell.git
   cd news-intell
   ```
3. Un environnement virtuel :
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux / macOS
   source .venv/bin/activate
   ```
4. Les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## 🐛 Créer une issue

- **Bug** : utilisez le [modèle de rapport de bug](.github/ISSUE_TEMPLATE/bug_report.yml)
  et fournissez un exemple minimal reproduisant le problème.
- **Fonctionnalité** : utilisez le [modèle de demande de fonctionnalité](.github/ISSUE_TEMPLATE/feature_request.yml).

Avant d'ouvrir une issue, recherchez s'il existe déjà une issue ouverte ou
fermée traitant du même sujet.

## 🌿 Travailler sur une branche

Créez une branche dédiée à partir de `main` :

```bash
git checkout -b feat/resume-ia
```

Nommez vos branches selon le schéma suivant :

| Préfixe     | Usage                             |
|-------------|-----------------------------------|
| `feat/`     | Nouvelle fonctionnalité           |
| `fix/`      | Correction de bug                 |
| `docs/`     | Documentation                     |
| `refactor/` | Refactorisation sans changement   |
| `test/`     | Ajout ou correction de tests      |

## 📝 Conventions de commit

Adoptez des messages clairs et, si possible, suivez les conventions
*Conventional Commits* :

```
feat: ajouter un agent de traduction
fix: corriger l'analyse des flux Atom
docs: documenter la configuration des sources
test: ajouter des tests sur l'extraction d'entités
```

Décrivez **quoi** et **pourquoi**, pas seulement comment.

## 🧪 Tests

Avant de proposer un changement, assurez-vous que les tests passent :

```bash
python -m unittest discover -s tests
```

Ajoutez des tests pour toute nouvelle fonctionnalité ou correction dans le
répertoire [`tests/`](tests).

## 🎨 Style de code

- La langue du code, des commentaires et des sorties est le **français**.
- Le projet utilise des conventions lisibles et sans dépendance inutile :
  docstrings en français, noms explicites, code typé (`from __future__ import annotations`).
- Privilégiez la bibliothèque standard ; les dépendances externes sont
  déclarées dans [`requirements.txt`](requirements.txt).

## 🔀 Ouvrir une pull request

1. Poussez votre branche :
   ```bash
   git push origin ma-branche
   ```
2. Ouvrez une pull request vers `main` en utilisant le
   [modèle de pull request](.github/PULL_REQUEST_TEMPLATE.md).
3. Décrivez clairement le changement et rappelez les issues concernées
   (ex. `Closes #12`).
4. La **CI** (`Tests`) doit passer avant la fusion.

## 📄 Code de conduite

En participant à ce projet, vous vous engagez à respecter notre
[Code de conduite](CODE_OF_CONDUCT.md).
