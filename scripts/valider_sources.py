"""Vérifie que les flux RSS configurés renvoient bien des articles.

Usage :
    python scripts/valider_sources.py
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJET = Path(__file__).resolve().parent.parent
if str(PROJET) not in sys.path:
    sys.path.insert(0, str(PROJET))

from news_intell.config import Config  # noqa: E402
from news_intell.sources import rss  # noqa: E402


def principale() -> int:
    """Parcourt la configuration et affiche le nombre d'articles par source."""
    config = Config.charger()
    ok = 0
    vides: list[str] = []

    for source in config.sources:
        nom = source.get("nom", source.get("url"))
        url = source.get("url")
        articles = rss.recuperer_flux(url, nom, timeout=12)
        print(f"{len(articles):>3}  {nom:<14}  {url}")
        if articles:
            ok += 1
        else:
            vides.append(str(nom))

    print(f"Sources OK : {ok}/{len(config.sources)}")
    if vides:
        print("Vides/erreurs :", ", ".join(vides))
    return 0


if __name__ == "__main__":
    raise SystemExit(principale())
