"""Agent d'analyse des techniques de communication (PNL « neuro »)."""
from __future__ import annotations

from typing import Any

from ...models import AnalyseArticle, Article
from .base import AgentPNL

SYSTEME_NEURO = (
    "Tu es un analyste francophone spécialiste de la Programmation "
    "Neuro-Linguistique (PNL) et de la communication persuasive. Analyse "
    "l'article pour identifier les techniques d'influence CONSTRUCTIVES "
    "utilisées (rapport, recadrage, ancrage, calibrage, présuppositions, "
    "questions hypnotiques, storytelling, métaphores, …). Réponds uniquement "
    "avec un objet JSON au format exact : "
    '{"neuro": [{"technique": "...", "exemple": "...", "description": "..."}]}. '
    "Les libellés sont en français, courts et factuels."
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
