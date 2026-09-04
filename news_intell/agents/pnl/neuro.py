"""Agent d'analyse des techniques de communication (PNL « neuro »)."""
from __future__ import annotations

from typing import Any

from ...models import AnalyseArticle, Article
from .base import AgentPNL

SYSTEME_NEURO = (
    "Tu es un spécialiste francophone en communication, rhétorique et Programmation "
    "Neuro-Linguistique (PNL), cultivé et méthodique. Analyse l'article pour "
    "identifier les techniques d'influence CONSTRUCTIVES employées (rapport, "
    "recadrage, ancrage, calibrage, présuppositions, questions hypnotiques, "
    "storytelling, métaphores, analogies…), en citant un exemple précis issu du "
    "texte. Réponds uniquement avec un objet JSON au format exact : "
    '{"neuro": [{"technique": "...", "exemple": "...", "description": "..."}]}. '
    "Les libellés sont en français, précis et factuels."
)


class AgentPNLNeuro(AgentPNL):
    """Repère les techniques de communication et d'influence constructives."""

    nom = "pnl_neuro"
    role = "Analyse des techniques de communication (PNL neuro)"
    categorie = "neuro"
    domaine = "Communication & influence constructive"

    def executer(
        self,
        article: Article,
        analyse: AnalyseArticle | None = None,
    ) -> dict[str, Any]:
        contenu = article.contenu or article.resume or article.titre
        contexte = ""
        if analyse is not None and analyse.thematique:
            contexte = f"\n\nThématique supposée : {analyse.thematique}."
        utilisateur = (
            f"Titre : {article.titre}\n\n"
            f"Source : {article.source}{contexte}\n\n"
            f"Contenu :\n{contenu[:6000]}"
        )
        donnees = self.json_strict(SYSTEME_NEURO, utilisateur)
        return {"neuro": donnees.get("neuro", [])}
