"""Agent d'extraction d'entités nommées et de mots-clés."""
from __future__ import annotations

from typing import Any

from ..models import Article
from .base import Agent

SYSTEME = (
    "Tu es un expert français du traitement automatique du langage. "
    "Extrais de l'article : les personnes, les organisations, les lieux et les mots-clés. "
    "Réponds uniquement avec un objet JSON au format exact : "
    '{"entites": {"personnes": [], "organisations": [], "lieux": []}, "mot_cle": []}. '
    "Chaque entité est une courte chaîne en français."
)


class AgentEntites(Agent):
    """Extrait les entités nommées et les mots-clés d'un article."""

    nom = "entites"
    role = "Extraction d'entités nommées et mots-clés"

    def executer(self, article: Article) -> dict[str, Any]:
        contenu = article.contenu or article.resume or article.titre
        utilisateur = f"Titre : {article.titre}\n\nContenu :\n{contenu[:6000]}"
        donnees = self.json_strict(SYSTEME, utilisateur)
        entites = donnees.get("entites", {}) or {}
        return {
            "entites": {
                "personnes": entites.get("personnes", []),
                "organisations": entites.get("organisations", []),
                "lieux": entites.get("lieux", []),
            },
            "mot_cle": donnees.get("mot_cle", []),
        }
