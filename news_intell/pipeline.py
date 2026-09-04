"""Pipeline haut niveau du projet news-intell.

Enchaîne : récupération des sources -> analyse par les agents -> stockage
-> génération du rapport.
"""
from __future__ import annotations

from pathlib import Path

from .agents.coordinator import CoordinateurAgents
from .client import LocalAIClient
from .config import Config
from .models import AnalyseArticle
from .output import generer_rapport
from .sources import rss
from .storage import sauvegarder_articles, sauvegarder_resultats


class Pipeline:
    """Orchestration complète du flux d'analyse de news."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = LocalAIClient(config)
        self.coordinateur = CoordinateurAgents(self.client, config)

    def recuperer(self) -> list:
        """Récupère les articles depuis toutes les sources configurées."""
        articles = []
        for source in self.config.sources:
            url = source.get("url")
            nom_source = source.get("nom", url)
            limite = int(source.get("limite", 20))
            recups = rss.recuperer_flux(url, nom_source)[:limite]
            articles.extend(recups)
        return self._dedupliquer(articles)

    @staticmethod
    def _dedupliquer(articles: list) -> list:
        """Supprime les doublons (par URL) en conservant le premier trouvé."""
        vus: set[str] = set()
        uniques = []
        for article in articles:
            if article.url and article.url not in vus:
                vus.add(article.url)
                uniques.append(article)
        return uniques

    def analyser(self, articles: list) -> list[AnalyseArticle]:
        """Analyse les articles et agrège les résultats."""
        return self.coordinateur.analyser_lot(articles)

    def executer(
        self,
        chemin_articles: Path | None = None,
        chemin_resultats: Path | None = None,
        format_rapport: str = "md",
    ) -> list[AnalyseArticle]:
        """Exécute le pipeline complet (récupération + analyse + stockage + rapport)."""
        articles = self.recuperer()
        chemin_articles = chemin_articles or Path("data") / "articles.json"
        sauvegarder_articles(articles, chemin_articles)

        resultats = self.analyser(articles)
        chemin_resultats = chemin_resultats or Path("data") / "resultats.json"
        sauvegarder_resultats(resultats, chemin_resultats)

        generer_rapport(resultats, chemin_resultats.parent, format_rapport)
        return resultats
