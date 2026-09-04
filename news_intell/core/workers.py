"""Travailleurs (workers) : production de l'analyse complète des news.

Un « travailleur » enchaîne l'analyse de base (agents classiques), l'équipe
PNL (analyse comportementale) puis la rédaction de la note par l'analyste.
"""
from __future__ import annotations

from ..agents.coordinator import CoordinateurAgents
from ..agents.pnl import EquipePNL
from ..client import LocalAIClient
from ..config import Config
from ..models import AnalyseArticle, Article
from .analyst import Analyste


class Travailleur:
    """Produit l'analyse complète d'un article de news."""

    def __init__(self, client: LocalAIClient, config: Config) -> None:
        self.coordinateur = CoordinateurAgents(client, config)
        self.equipe_pnl = EquipePNL(client, config)
        self.analyste = Analyste(client, config)
        self._pnl_actif = bool(getattr(config, "pnl_active", True))

    def traiter(self, article: Article) -> AnalyseArticle:
        """Enchaîne l'analyse de base, PNL et la rédaction de la note."""
        analyse = self.coordinateur.analyser(article)
        if self._pnl_actif:
            try:
                analyse.pnl = self.equipe_pnl.analyser(article, analyse)
            except Exception as exc:  # noqa: BLE001
                analyse.erreurs.append(f"pnl : {exc}")
            try:
                analyse.note_analyste = self.analyste.rediger(article, analyse, analyse.pnl)
            except Exception as exc:  # noqa: BLE001
                analyse.erreurs.append(f"analyste : {exc}")
        return analyse


class ParcTravailleurs:
    """Distribue les articles entre plusieurs travailleurs."""

    def __init__(self, client: LocalAIClient, config: Config, nb: int = 1) -> None:
        self._travailleurs = [Travailleur(client, config) for _ in range(max(1, nb))]
        self._index = 0

    def traiter(self, article: Article) -> AnalyseArticle:
        """Confie un article au prochain travailleur (roulement)."""
        travailleur = self._travailleurs[self._index]
        self._index = (self._index + 1) % len(self._travailleurs)
        return travailleur.traiter(article)

    def traiter_lot(self, articles: list[Article]) -> list[AnalyseArticle]:
        """Traite une liste d'articles et renvoie les analyses."""
        return [self.traiter(article) for article in articles]
