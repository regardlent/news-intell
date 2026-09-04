"""Recherche d'articles (texte + sémantique par reranker / embeddings)."""
from __future__ import annotations

from typing import Any

from ..client import LocalAIClient
from ..semantic import similarite_cosinus


def _texte_article(a: dict[str, Any]) -> str:
    """Construit le texte indexable d'une analyse."""
    parties = [
        a.get("titre", ""),
        a.get("resume_ia", ""),
        a.get("resume", ""),
        a.get("thematique", ""),
    ]
    return " ".join(partie for partie in parties if partie)


def rechercher_texte(articles: list[dict[str, Any]], q: str) -> list[dict[str, Any]]:
    """Filtrage par correspondance textuelle simple."""
    qn = q.strip().lower()
    if not qn:
        return articles

    def correspond(a: dict[str, Any]) -> bool:
        champs = [
            a.get("titre", ""),
            a.get("thematique", ""),
            a.get("source", ""),
            " ".join(a.get("mot_cle", [])),
        ]
        return any(qn in champ.lower() for champ in champs)

    return [a for a in articles if correspond(a)]


def rechercher_semantique(
    articles: list[dict[str, Any]],
    q: str,
    client: LocalAIClient,
    top_n: int | None = None,
) -> list[dict[str, Any]]:
    """Classe les articles par pertinence pour la requête (reranker, repli embeddings).

    Si l'appel au reranker échoue, bascule sur la similarité de cosinus ; en
    dernier recours, revient au filtrage textuel.
    """
    if not articles:
        return []
    documents = [_texte_article(a) for a in articles]

    scores = None
    try:
        scores = client.reranker(q, documents)
    except Exception:  # noqa: BLE001
        scores = None

    if scores is None:
        try:
            vecteur_requete = client.embedding(q)
            scores = [
                similarite_cosinus(vecteur_requete, client.embedding(d)) for d in documents
            ]
        except Exception:  # noqa: BLE001
            return rechercher_texte(articles, q)

    apparies = sorted(zip(articles, scores), key=lambda paire: paire[1], reverse=True)
    if top_n:
        apparies = apparies[:top_n]
    return [a for a, _ in apparies]
