"""Agent d'évaluation de la pertinence d'un article."""
from __future__ import annotations

from typing import Any

from ..models import Article
from .base import Agent

SYSTEME = (
    "Tu es un rédacteur en chef et un éditorialiste expérimenté, cultivé et exigeant. "
    "Évalue l'importance et la pertinence de l'article pour un lectorat général sur "
    "une échelle de 0.0 (anecdotique) à 1.0 (majeur), en pesant l'impact, la portée "
    "et l'intérêt public. Réponds uniquement avec un objet JSON au format exact : "
    '{"pertinence": 0.5}.'
)


class AgentPertinence(Agent):
    """Note l'importance d'un article pour un lectorat général."""

    nom = "pertinence"
    role = "Évaluation de la pertinence de l'article"

    def executer(self, article: Article) -> dict[str, Any]:
        contenu = article.contenu or article.resume or article.titre
        utilisateur = f"Titre : {article.titre}\n\nContenu :\n{contenu[:6000]}"
        donnees = self.json_strict(SYSTEME, utilisateur)
        try:
            score = float(donnees.get("pertinence", 0.0))
        except (TypeError, ValueError):
            score = 0.0
        return {"pertinence": max(0.0, min(1.0, score))}
