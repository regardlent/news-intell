"""Agent de classification thématique des articles."""
from __future__ import annotations

from typing import Any

from ..models import Article
from .base import Agent

SYSTEME = (
    "Tu es un spécialiste français de l'analyse de l'actualité. "
    "Classe l'article fourni dans UNE thématique principale ET dans des "
    "catégories secondaires. Réponds uniquement avec un objet JSON au format exact : "
    '{"thematique": "...", "categories": ["cat1", "cat2"]}. '
    "Les libellés doivent être en français, courts et génériques."
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
