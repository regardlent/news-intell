"""Agent d'analyse de sentiment des articles."""
from __future__ import annotations

from typing import Any

from ..models import Article
from .base import Agent

SYSTEME = (
    "Tu es un analyste francophone du ton éditorial. "
    "Évalue le sentiment général de l'article sur une échelle de -1.0 (très négatif) "
    "à +1.0 (très positif) et fournis un libellé parmi : 'positif', 'neutre' ou 'negatif'. "
    "Réponds uniquement avec un objet JSON au format exact : "
    '{"sentiment": "neutre", "score_sentiment": 0.0}.'
)


class AgentSentiment(Agent):
    """Détermine le ton général d'un article."""

    nom = "sentiment"
    role = "Analyse du sentiment de l'article"

    def executer(self, article: Article) -> dict[str, Any]:
        contenu = article.contenu or article.resume or article.titre
        utilisateur = f"Titre : {article.titre}\n\nContenu :\n{contenu[:6000]}"
        donnees = self.json_strict(SYSTEME, utilisateur)
        libelle = donnees.get("sentiment", "neutre")
        if libelle not in ("positif", "neutre", "negatif"):
            libelle = "neutre"
        try:
            score = float(donnees.get("score_sentiment", 0.0))
        except (TypeError, ValueError):
            score = 0.0
        return {"sentiment": libelle, "score_sentiment": max(-1.0, min(1.0, score))}
