"""Pipeline haut niveau du projet news-intell.

Enchaîne : récupération des sources -> analyse par les agents -> stockage
-> génération du rapport.
"""
from __future__ import annotations

from pathlib import Path

from . import semantic
from .config import Config
from .core.workers import ParcTravailleurs
from .llm import creer_llm
from .models import AnalyseArticle
from .output import generer_rapport
from .sources import rss
from .storage import sauvegarder_articles, sauvegarder_resultats


class Pipeline:
    """Orchestration complète du flux d'analyse de news."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = creer_llm(config)
        self.parc = ParcTravailleurs(self.client, config, config.nb_workers)

    def recuperer(self) -> list:
        """Récupère les articles depuis toutes les sources configurées."""
        articles = []
        for source in self.config.sources:
            url = source.get("url")
            nom_source = source.get("nom", url)
            limite = int(source.get("limite", 20))
            recups = rss.recuperer_flux(url, nom_source)[:limite]
            articles.extend(recups)
        articles = self._dedupliquer(articles)
        if self.config.dedupe_active:
            try:
                articles = semantic.dedupliciter(
                    articles, self.client, self.config.dedupe_seuil
                )
            except Exception as exc:  # noqa: BLE001
                print(f"⚠ Déduplication sémantique ignorée : {exc}")
        return articles

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
        return self.parc.traiter_lot(articles)

    def _applique_groupes(self, resultats: list[AnalyseArticle], articles: list) -> None:
        """Assigné un identifiant de groupe (sujet sémantique) à chaque analyse."""
        try:
            groupes = semantic.groupes_ordonnes(
                articles, self.client, self.config.clustering_seuil
            )
        except Exception as exc:  # noqa: BLE001
            print(f"⚠ Regroupement sémantique ignoré : {exc}")
            return
        assignations: dict[int, int] = {}
        for numero, membres in enumerate(groupes, start=1):
            for article in membres:
                assignations[id(article)] = numero
        for resultat in resultats:
            resultat.groupe = assignations.get(id(resultat.article), 0)

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
        if self.config.clustering_active:
            self._applique_groupes(resultats, articles)
        chemin_resultats = chemin_resultats or Path("data") / "resultats.json"
        sauvegarder_resultats(resultats, chemin_resultats)

        generer_rapport(resultats, chemin_resultats.parent, format_rapport)
        return resultats
