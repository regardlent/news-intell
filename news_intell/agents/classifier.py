"""Agent de classification thématique des articles."""
from __future__ import annotations

from typing import Any

from ..models import Article
from .base import Agent

SYSTEME = (
    "Tu es un expert en sciences sociales et en analyse de l'actualité, cultivé et "
    "exigeant. Classe l'article dans UNE thématique principale pertinente et dans "
    "des catégories secondaires précises (économie, politique, climat, société, "
    "culture, sport, international…). Réponds uniquement avec un objet JSON au "
    "format exact : "
    '{"thematique": "...", "categories": ["cat1", "cat2"]}. '
    "Les libellés sont en français, courts, précis et génériques."
)


class AgentClassification(Agent):
    """Détermine la thématique principale et les catégories d'un article."""

    nom = "classification"
    role = "Classification thématique de l'article"

    def executer(self, article: Article) -> dict[str, Any]:
        contenu = article.contenu or article.resume or article.titre
        utilisateur = f"Titre : {article.titre}\n\nContenu :\n{contenu[:6000]}"
        donnees = self.json_strict(SYSTEME, utilisateur)
        return {
            "thematique": donnees.get("thematique", ""),
            "categories": donnees.get("categories", []),
        }
