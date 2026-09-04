"""Base des agents PNL (Programmation Neuro-Linguistique).

Les agents PNL analysent le discours des news sous l'angle de la
communication (PNL « neuro ») et des procédés manipulateurs (PNL « noir »).
"""
from __future__ import annotations

from typing import Any

from ...client import LocalAIClient
from ...config import Config
from ...models import AnalyseArticle, Article
from ..base import Agent


class AgentPNL(Agent):
    """Agent spécialisé en Programmation Neuro-Linguistique.

    Attributs de classe :
        categorie: famille de l'agent (« neuro » ou « noir »).
        domaine: sous-domaine d'analyse (libellé en français).
    """

    categorie: str = ""
    domaine: str = ""

    def __init__(self, client: LocalAIClient, config: Config) -> None:
        super().__init__(client, config)

    def executer(
        self,
        article: Article,
        analyse: AnalyseArticle | None = None,
    ) -> dict[str, Any]:
        """Analyse comportementale d'un article (à surcharger)."""
        raise NotImplementedError
