"""Persistance et chargement des articles et des résultats d'analyse."""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import AnalyseArticle, Article


def sauvegarder_articles(articles: list["Article"], chemin: Path) -> Path:
    """Écrit les articles bruts dans un fichier JSON."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    donnees = [a.vers_dict() for a in articles]
    chemin.write_text(
        json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return chemin


def charger_articles(chemin: Path) -> list["Article"]:
    """Recharge des articles bruts depuis un fichier JSON."""
    chemin = Path(chemin)
    if not chemin.exists():
        return []
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    from .models import Article

    return [Article.depuis_dict(d) for d in donnees]


def sauvegarder_resultats(resultats: list["AnalyseArticle"], chemin: Path) -> Path:
    """Écrit les résultats d'analyse dans un fichier JSON."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    donnees = [r.vers_dict() for r in resultats]
    chemin.write_text(
        json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return chemin


def charger_resultats(chemin: Path) -> list[dict]:
    """Recharge les résultats d'analyse depuis un fichier JSON."""
    chemin = Path(chemin)
    if not chemin.exists():
        return []
    return json.loads(chemin.read_text(encoding="utf-8"))
