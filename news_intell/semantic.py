"""Analyse sémantique : déduplication et regroupement d'articles via embeddings.

S'appuie sur le modèle d'embedding de LocalAI (`modele_embedding`) pour
rapprocher les articles par similarité de cosinus, et permettre la
déduplication et le regroupement thématique.
"""
from __future__ import annotations

import math

from .client import LocalAIClient
from .models import Article


def _texte_a_embedder(article: Article) -> str:
    """Construit le texte à vectoriser (titre + résumé + source + début du contenu)."""
    parties = [article.titre, article.resume, article.source]
    if article.contenu:
        parties.append(article.contenu[:600])
    return " ".join(partie for partie in parties if partie)


def vectoriser(article: Article, client: LocalAIClient) -> list[float]:
    """Calcule le vecteur d'embedding d'un article."""
    return client.embedding(_texte_a_embedder(article))


def similarite_cosinus(a: list[float], b: list[float]) -> float:
    """Similarité de cosinus entre deux vecteurs (dans [-1, 1])."""
    if not a or not b or len(a) != len(b):
        return 0.0
    norme_a = math.sqrt(sum(x * x for x in a))
    norme_b = math.sqrt(sum(x * x for x in b))
    if norme_a == 0.0 or norme_b == 0.0:
        return 0.0
    produit = sum(x * y for x, y in zip(a, b))
    return produit / (norme_a * norme_b)


def dedupliciter(
    articles: list[Article],
    client: LocalAIClient,
    seuil: float = 0.9,
) -> list[Article]:
    """Supprime les doublons sémantiques en conservant le premier de chaque groupe.

    Args:
        articles: articles ([potentiellement] doublons) à filtrer.
        client: client LocalAI (pour l'embedding).
        seuil: similarité minimale pour considérer deux articles comme doublons.
    """
    gardes: list[Article] = []
    vecteurs: list[list[float]] = []
    for article in articles:
        vecteur = vectoriser(article, client)
        if any(similarite_cosinus(vecteur, v) >= seuil for v in vecteurs):
            continue
        gardes.append(article)
        vecteurs.append(vecteur)
    return gardes


def regrouper(
    articles: list[Article],
    client: LocalAIClient,
    seuil: float = 0.7,
) -> dict[int, list[Article]]:
    """Regroupe les articles similaires en clusters (composantes connexes).

    Returns:
        Dictionnaire {racine_de_cluster: [articles]}.
    """
    vecteurs = [vectoriser(article, client) for article in articles]
    n = len(articles)
    parents = list(range(n))

    def trouver(i: int) -> int:
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    def unir(i: int, j: int) -> None:
        ri, rj = trouver(i), trouver(j)
        if ri != rj:
            parents[ri] = rj

    for i in range(n):
        for j in range(i + 1, n):
            if similarite_cosinus(vecteurs[i], vecteurs[j]) >= seuil:
                unir(i, j)

    groupes: dict[int, list[Article]] = {}
    for i, article in enumerate(articles):
        groupes.setdefault(trouver(i), []).append(article)
    return groupes


def groupes_ordonnes(
    articles: list[Article],
    client: LocalAIClient,
    seuil: float = 0.7,
) -> list[list[Article]]:
    """Renvoie les groupes triés du plus grand au plus petit."""
    clusters = regrouper(articles, client, seuil)
    return sorted(clusters.values(), key=len, reverse=True)
