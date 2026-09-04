"""Statistiques du tableau de bord (sources, thèmes, sentiments, mots-clés)."""
from __future__ import annotations

from collections import Counter
from typing import Any


def _est_nombre(valeur: Any) -> bool:
    return isinstance(valeur, (int, float))


def calculer_statistiques(articles: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcule les indicateurs du tableau de bord à partir des analyses."""
    par_source = Counter(a.get("source", "Inconnu") for a in articles)
    par_theme = Counter(a.get("thematique", "Divers") for a in articles)
    par_sentiment = Counter(a.get("sentiment", "neutre") for a in articles)

    mots: Counter[str] = Counter()
    for article in articles:
        for mot in article.get("mot_cle", []):
            if mot:
                mots[mot] += 1

    pertinences = [
        float(a.get("pertinence", 0.0)) for a in articles if _est_nombre(a.get("pertinence"))
    ]
    moyenne = sum(pertinences) / len(pertinences) if pertinences else 0.0

    return {
        "par_source": par_source.most_common(),
        "par_theme": par_theme.most_common(),
        "par_sentiment": par_sentiment.most_common(),
        "mots_courants": mots.most_common(10),
        "moyenne_pertinence": round(moyenne, 2),
    }
