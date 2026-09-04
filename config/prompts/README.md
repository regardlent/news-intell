# Ce dossier contient les prompts (en français) utilisés par les agents IA.

## Remarque sur l'emplacement des prompts

Dans cette version du projet, les prompts sont définis directement dans le
code de chaque agent (constante `SYSTEME` du module `news_intell/agents/*.py`) afin de
rester simple et lisible.

Cette architecture permet de retrouver facilement l'instruction système de chaqune
mission au même endroit que sa logique.

Vous trouverez ici un emplacement de référence pour externaliser ces prompts
dans des fichiers texte (`.md` ou `.txt`) si vous souhaitez les rendre
modifiables sans toucher au code.

### Missions couvertes

| Agent            | Fichier de code                        | Mission                                       |
|------------------|----------------------------------------|-----------------------------------------------|
| Résumé           | `news_intell/agents/summarizer.py`             | Résumer un article en 2 à 4 phrases            |
| Classification   | `news_intell/agents/classifier.py`             | Thématique principale + catégories             |
| Sentiment        | `news_intell/agents/sentiment.py`              | Ton (positif, neutre, négatif) + score (-1..1) |
| Entités          | `news_intell/agents/entities.py`               | Personnes, organisations, lieux, mots-clés     |
| Pertinence       | `news_intell/agents/relevance.py`              | Note d'importance (0..1)                       |
