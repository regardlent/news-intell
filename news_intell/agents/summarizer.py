"""Agent de résumé automatique des articles de presse."""
from __future__ import annotations

from typing import Any

from ..models import Article
from .base import Agent

SYSTEME = (
    "Tu es un journaliste et analyste éditorial chevronné, cultivé et rigoureux, "
    "rompu à la synthèse de l'actualité francophone. Rédige un résumé précis, "
    "nuancé et factuel de l'article fourni, en deux à quatre phrases. Distingue "
    "les faits vérifiés des hypothèses et citations, et précise le contexte "
    "essentiel. Réponds uniquement avec le texte du résumé."
)


class AgentResume(Agent):
    """Produit un résumé synthétique de l'article."""

    nom = "resume"
    role = "Résumé automatique de l'article"

    def executer(self, article: Article) -> dict[str, Any]:
        contenu = article.contenu or article.resume or article.titre
        utilisateur = (
            f"Titre : {article.titre}\n\n"
            f"Source : {article.source}\n\n"
            f"Contenu de l'article :\n{contenu[:6000]}"
        )
        resume = self.generer(SYSTEME, utilisateur)
        return {"resume_ia": resume}
