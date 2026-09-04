"""Interface en ligne de commande du projet news-intell.

Usage :
    python -m news_intell.cli recuperer
    python -m news_intell.cli analyser --fichier data/articles.json
    python -m news_intell.cli executer --format md
    python -m news_intell.cli lister-modeles
    python -m news_intell.cli serveur --hote 127.0.0.1 --port 8000
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .client import LocalAIClient
from .config import Config
from .output import generer_rapport
from .pipeline import Pipeline
from .storage import charger_articles, sauvegarder_articles, sauvegarder_resultats


def _config() -> Config:
    return Config.charger()


def cmd_recuperer(_args) -> int:
    """Récupère et stocke les articles issus des sources configurées."""
    pipeline = Pipeline(_config())
    articles = pipeline.recuperer()
    chemin = sauvegarder_articles(articles, Path("data") / "articles.json")
    print(f"✔ Récupération terminée : {len(articles)} article(s) récupéré(s).")
    print(f"   Fichier : {chemin}")
    for article in articles:
        print(f"   - [{article.source}] {article.titre}")
    return 0


def cmd_analyser(args) -> int:
    """Analyse les articles précédemment récupérés."""
    articles = charger_articles(Path(args.fichier))
    if not articles:
        print("Aucun article à analyser. Lancez d'abord la commande « recuperer ».")
        return 1
    pipeline = Pipeline(_config())
    print(f"Analyse de {len(articles)} article(s)…")
    resultats = pipeline.analyser(articles)
    chemin = sauvegarder_resultats(resultats, Path("data") / "resultats.json")
    generer_rapport(resultats, Path("data"), args.format)
    print(f"✔ Analyse terminée : {len(resultats)} article(s) analysé(s).")
    print(f"   Résultats : {chemin}")
    return 0


def cmd_executer(args) -> int:
    """Exécute le pipeline complet : récupération + analyse + rapport."""
    pipeline = Pipeline(_config())
    print("Exécution du pipeline complet…")
    resultats = pipeline.executer(format_rapport=args.format)
    print(f"✔ Pipeline terminé : {len(resultats)} article(s) analysé(s).")
    print("   Rapport généré dans le dossier « data/ ».")
    return 0


def cmd_lister_modeles(_args) -> int:
    """Liste les modèles disponibles sur le serveur LocalAI."""
    client = LocalAIClient(_config())
    try:
        modeles = client.lister_modeles()
    except Exception as exc:  # noqa: BLE001
        print(f"✖ Impossible de lister les modèles : {exc}", file=sys.stderr)
        return 1
    print("Modèles disponibles sur LocalAI :")
    for modele in modeles:
        print(f"   - {modele.get('id', modele)}")
    return 0


def cmd_serveur(args) -> int:
    """Lance l'interface web (FastAPI + uvicorn)."""
    try:
        import uvicorn  # noqa: WPS433
    except ImportError as exc:  # noqa: BLE001, F821
        print(
            f"✖ Dépendance manquante pour le serveur web : {exc}. "
            "Installez « pip install -e .[web] ».",
            file=sys.stderr,
        )
        return 1
    uvicorn.run(
        "news_intell.web.app:app",
        host=args.hote,
        port=args.port,
        reload=args.recharger,
    )
    return 0


def construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(
        prog="news-intell",
        description="Analyse intelligente de l'actualité par des agents IA (LocalAI).",
    )
    sous = parseur.add_subparsers(dest="commande", required=True)

    sous.add_parser("recuperer", help="Récupère les articles des sources configurées.")

    parser_analyse = sous.add_parser(
        "analyser", help="Analyse les articles précédemment récupérés."
    )
    parser_analyse.add_argument(
        "--fichier",
        default="data/articles.json",
        help="Fichier JSON des articles à analyser.",
    )
    parser_analyse.add_argument(
        "--format",
        default="md",
        choices=["md", "csv", "html"],
        help="Format du rapport généré.",
    )

    parser_executer = sous.add_parser("executer", help="Exécute le pipeline complet.")
    parser_executer.add_argument(
        "--format",
        default="md",
        choices=["md", "csv", "html"],
        help="Format du rapport généré.",
    )

    sous.add_parser(
        "lister-modeles", help="Liste les modèles disponibles sur LocalAI."
    )

    parser_serveur = sous.add_parser("serveur", help="Lance l'interface web (FastAPI).")
    parser_serveur.add_argument("--hote", default="127.0.0.1", help="Adresse d'écoute.")
    parser_serveur.add_argument("--port", default=8000, type=int, help="Port d'écoute.")
    parser_serveur.add_argument(
        "--recharger", action="store_true", help="Rechargement automatique (dev)."
    )

    return parseur


def main(argv: list[str] | None = None) -> int:
    parseur = construire_parseur()
    args = parseur.parse_args(argv)
    commandes = {
        "recuperer": cmd_recuperer,
        "analyser": cmd_analyser,
        "executer": cmd_executer,
        "lister-modeles": cmd_lister_modeles,
        "serveur": cmd_serveur,
    }
    try:
        return commandes[args.commande](args)
    except Exception as exc:  # noqa: BLE001
        print(f"✖ Erreur : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
