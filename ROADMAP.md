# Feuille de route — news-intell

Ce document décrit la vision et les prochaines étapes du projet. Il est
susceptible d'évoluer au fil des retours de la communauté.

## 🧭 Vision

Permettre à chacun d'analyser automatiquement l'actualité **en français** grâce
à des agents IA locaux (LocalAI), sans dépendre d'un service cloud, avec une
forte attention à la simplicité et à la lisibilité.

## 📈 Phases

### Phase 1 — Socle (terminée ✅)
- Collecte RSS / Atom multi-sources.
- Pipeline d'agents IA (résumé, thème, sentiment, entités, pertinence).
- Stockage JSON et rapports Markdown / CSV / HTML.
- CLI, configuration, tests et CI.

### Phase 2 — Amélioration de l'analyse (en cours 🔄)
- [x] Analyse comportementale : équipe **PNL** (« neuro » / « noir ») + **Analyste** (note écrite) + travailleurs.
- [ ] Agent de **traduction** pour normaliser des articles multilingues.
- [x] **Déduplication sémantique** via embeddings (`hal-qwen3-embedding-0.6b`).
- [x] Regroupement en **clusters thématiques** (groupes de sujet).
- [ ] Détection de **tendance** (sujets en forte progression).
- [x] Interface **web** (FastAPI) : lecture journalistique + administration.

### Phase 3 — Exploitation (à venir 📅)
- [ ] Planification automatique des analyses (cron / tâche planifiée).
- [ ] Tableau de bord **HTML** enrichi (filtres, recherche, graphiques).
- [ ] Alertes sur des sujets ou entités d'intérêt.
- [x] Empaquetage Python (`pyproject.toml`) et workflow de **release GitHub**.
- [ ] Publication PyPI éventuelle.

## 💡 Suggestions de la communauté

Cette section est alimentée par les demandes d'issues et directions proposées
par les contributeurs. N'hésitez pas à ouvrir une
[issue](https://github.com/regardlent/news-intell/issues) pour proposer une
nouvelle idée.
