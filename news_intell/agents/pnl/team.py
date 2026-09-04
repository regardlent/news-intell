"""Équipe d'agents PNL (neuro + noir) pour l'analyse comportementale."""
from __future__ import annotations

from typing import Any

from ...client import LocalAIClient
from ...config import Config
from ...models import AnalyseArticle, AnalysePNL, Article
from .base import AgentPNL
from .neuro import AgentPNLNeuro
from .noir import AgentPNLNoir

NIVEAUX = ("faible", "modéré", "élevé")


class EquipePNL:
    """Coordonne les agents PNL neuro et noir sur un article."""

    def __init__(self, client: LocalAIClient, config: Config) -> None:
        self._agents: list[AgentPNL] = [
            AgentPNLNeuro(client, config),
            AgentPNLNoir(client, config),
        ]

    def analyser(
        self,
        article: Article,
        analyse: AnalyseArticle | None = None,
    ) -> AnalysePNL:
        """Exécute les agents PNL et agrège le résultat comportemental."""
        resultats: dict[str, Any] = {}
        erreurs: list[str] = []
        for agent in self._agents:
            try:
                resultats.update(agent.executer(article, analyse))
            except Exception as exc:  # noqa: BLE001
                erreurs.append(f"{agent.nom} : {exc}")

        try:
            score = float(resultats.get("score_manipulation", 0.0))
        except (TypeError, ValueError):
            score = 0.0
        niveau = resultats.get("niveau_manipulation", "faible")
        if niveau not in NIVEAUX:
            niveau = "faible"

        return AnalysePNL(
            neuro=resultats.get("neuro", []),
            noir=resultats.get("noir", []),
            score_manipulation=max(0.0, min(1.0, score)),
            niveau_manipulation=niveau,
            boutons_chauds=resultats.get("boutons_chauds", []),
            remarques=resultats.get("remarques", ""),
            erreurs=erreurs,
        )
