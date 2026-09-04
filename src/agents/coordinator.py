"""Coordinateur multi-agents du projet news-intell.

Il orchestre l'exécution des agents sur chaque article et agrège le résultat.
"""
from __future__ import annotations

from typing import Any

from ..client import LocalAIClient
from ..config import Config
from ..models import AnalyseArticle, Article
from .base import Agent
from .classifier import AgentClassification
from .entities import AgentEntites
from .relevance import AgentPertinence
from .sentiment import AgentSentiment
from .summarizer import AgentResume


class CoordinateurAgents:
    """Séquence les agents IA pour enrichir un article."""

    def __init__(self, client: LocalAIClient, config: Config) -> None:
        self._client = client
        self._config = config
        # Ordre d'exécution : d'abord le résumé, puis les analyses thématiques.
        self._agents: list[Agent] = [
            AgentResume(client, config),
            AgentClassification(client, config),
            AgentSentiment(client, config),
            AgentEntites(client, config),
            AgentPertinence(client, config),
        ]

    def analyser(self, article: Article) -> AnalyseArticle:
        """Analyse un article et renvoie le résultat enrichi."""
        analyse = AnalyseArticle(article=article)
        for agent in self._agents:
            try:
                resultat = agent.executer(article)
                for cle, valeur in resultat.items():
                    setattr(analyse, cle, valeur)
            except Exception as exc:  # noqa: BLE001
                analyse.erreurs.append(f"{agent.nom} : {exc}")
        return analyse

    def analyser_lot(self, articles: list[Article]) -> list[AnalyseArticle]:
        """Analyse une liste d'articles et renvoie les résultats."""
        return [self.analyser(article) for article in articles]

    @property
    def agents(self) -> list[Agent]:
        """Renvoie la liste des agents gérés par le coordinateur."""
        return list(self._agents)
