"""Agent de détection des techniques de manipulation (PNL « noir »)."""
from __future__ import annotations

from typing import Any

from ...models import AnalyseArticle, Article
from .base import AgentPNL

NIVEAUX = ("faible", "modéré", "élevé")

SYSTEME_NOIR = (
    "Tu es un expert francophone en analyse du discours et des procédés dits "
    "« sombres » (dark patterns, neuromarketing, manipulation). Analyse "
    "l'article pour repérer les manipulations : appel à la peur, urgence "
    "artificielle, autorité ou rareté de façade, culpabilisation, gaslighting, "
    "langage biaisé, ambiguïté volontaire, généralisations abusives, flatterie "
    "excessive, … Réponds uniquement avec un objet JSON au format exact : "
    '{"noir": [{"technique": "...", "exemple": "...", '
    '"indice_manipulation": 0.0}], "score_manipulation": 0.0, '
    '"boutons_chauds": ["peur"], "niveau_manipulation": "faible"}. '
    "Le niveau est précisément « faible », « modéré » ou « élevé ». "
    "Les libellés sont en français, courts et factuels."
)


class AgentPNLNoir(AgentPNL):
    """Détecte les techniques de manipulation et d'influence sombres."""

    nom = "pnl_noir"
    role = "Détection des techniques de manipulation (PNL noir)"
    categorie = "noir"
    domaine = "Analyse des procédés manipulateurs"

    def executer(
        self,
        article: Article,
        analyse: AnalyseArticle | None = None,
    ) -> dict[str, Any]:
        contenu = article.contenu or article.resume or article.titre
        utilisateur = (
            f"Titre : {article.titre}\n\nSource : {article.source}\n\n"
            f"Contenu :\n{contenu[:6000]}"
        )
        donnees = self.json_strict(SYSTEME_NOIR, utilisateur)
        try:
            score = float(donnees.get("score_manipulation", 0.0))
        except (TypeError, ValueError):
            score = 0.0
        niveau = donnees.get("niveau_manipulation", "faible")
        if niveau not in NIVEAUX:
            niveau = "faible"
        return {
            "noir": donnees.get("noir", []),
            "score_manipulation": max(0.0, min(1.0, score)),
            "boutons_chauds": donnees.get("boutons_chauds", []),
            "niveau_manipulation": niveau,
            "remarques": donnees.get("remarques", ""),
        }
