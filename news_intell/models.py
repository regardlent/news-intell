"""Modèles de données du pipeline d'analyse de news.

Décrit un article de presse et le résultat d'analyse enrichi par les agents.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Article:
    """Un article de presse récupéré depuis une source."""

    titre: str
    url: str
    source: str
    resume: str = ""           # description / extrait fourni par la source
    contenu: str = ""          # texte complet (si disponible)
    date_publication: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def vers_dict(self) -> dict[str, Any]:
        """Sérialise l'article en dictionnaire (pour l'export JSON)."""
        return {
            "titre": self.titre,
            "url": self.url,
            "source": self.source,
            "resume": self.resume,
            "contenu": self.contenu,
            "date_publication": self.date_publication,
            "meta": self.meta,
        }

    @classmethod
    def depuis_dict(cls, donnees: dict[str, Any]) -> "Article":
        """Reconstruit un article depuis un dictionnaire."""
        return cls(
            titre=donnees.get("titre", ""),
            url=donnees.get("url", ""),
            source=donnees.get("source", ""),
            resume=donnees.get("resume", ""),
            contenu=donnees.get("contenu", ""),
            date_publication=donnees.get("date_publication", ""),
            meta=donnees.get("meta", {}),
        )


@dataclass
class AnalyseArticle:
    """Résultat de l'analyse d'un article par les agents IA."""

    article: Article
    resume_ia: str = ""
    thematique: str = ""
    categories: list[str] = field(default_factory=list)
    sentiment: str = ""
    score_sentiment: float = 0.0
    entites: dict[str, list[str]] = field(default_factory=dict)  # {type: [valeurs]}
    pertinence: float = 0.0
    mot_cle: list[str] = field(default_factory=list)
    erreurs: list[str] = field(default_factory=list)

    def vers_dict(self) -> dict[str, Any]:
        """Sérialise l'analyse en dictionnaire (pour l'export JSON)."""
        return {
            "titre": self.article.titre,
            "url": self.article.url,
            "source": self.article.source,
            "date_publication": self.article.date_publication,
            "resume": self.article.resume,
            "resume_ia": self.resume_ia,
            "thematique": self.thematique,
            "categories": self.categories,
            "sentiment": self.sentiment,
            "score_sentiment": self.score_sentiment,
            "entites": self.entites,
            "pertinence": self.pertinence,
            "mot_cle": self.mot_cle,
            "erreurs": self.erreurs,
        }
