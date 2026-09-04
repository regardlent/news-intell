"""Génère rapidement un jeu d'exemples (limité) pour alimenter l'interface.

Analyse un petit nombre d'articles (par défaut 4) sur les 2 premières sources,
en désactivant la déduplication/le regroupement sémantique pour rester rapide.

Usage :
    python scripts/generer_exemple.py [nb_articles]
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJET = Path(__file__).resolve().parent.parent
if str(PROJET) not in sys.path:
    sys.path.insert(0, str(PROJET))

from news_intell.config import AgentConfig, Config  # noqa: E402
from news_intell.output import generer_rapport  # noqa: E402
from news_intell.pipeline import Pipeline  # noqa: E402
from news_intell.storage import sauvegarder_resultats  # noqa: E402

# Compromis vitesse/qualité : un modèle léger (qwen3-1.7b) est le plus fiable
# ici pour produire des sorties JSON structurées non vides.
MODES = {nom: ("qwen3-1.7b", 0.3) for nom in (
    "_defaut", "resume", "classification", "sentiment", "entites",
    "pertinence", "pnl_neuro", "pnl_noir", "analyste",
)}


def principale(nb: int = 2) -> int:
    """Analyse un petit lot d'articles et écrit data/resultats.json + rapport."""
    config = Config.charger()
    config.dedupe_active = False
    config.clustering_active = False
    config.pnl_active = True
    config.nb_workers = 1
    config.sources = [dict(source) for source in config.sources[:2]]
    for source in config.sources:
        source["limite"] = max(1, nb // len(config.sources))
    for nom, (modele, temperature) in MODES.items():
        config.agents[nom] = AgentConfig(modele=modele, temperature=temperature)

    pipeline = Pipeline(config)
    print(f"Récupération… ({len(config.sources)} source(s))", flush=True)
    articles = pipeline.recuperer()
    print(f"  {len(articles)} article(s) récupéré(s)", flush=True)

    resultats = []
    for i, article in enumerate(articles, start=1):
        print(f"  Analyse {i}/{len(articles)} : {article.titre[:40]}", flush=True)
        resultats.append(pipeline.parc.traiter(article))

    sauvegarder_resultats(resultats, Path("data") / "resultats.json")
    generer_rapport(resultats, Path("data"), "md")
    print(f"OK : {len(resultats)} article(s) analysé(s) -> data/resultats.json", flush=True)
    return 0


if __name__ == "__main__":
    nb = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    raise SystemExit(principale(nb))
