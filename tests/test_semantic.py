"""Tests du module d'analyse sémantique (déduplication, regroupement)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Ajoute la racine du projet au PATH pour pouvoir importer le module « news_intell ».
RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from news_intell.models import Article
from news_intell.semantic import (
    dedupliciter,
    groupes_ordonnes,
    similarite_cosinus,
    vectoriser,
)


class FakeEmbedding:
    """Client LocalAI simulé : renvoie un vecteur selon le texte fourni."""

    def __init__(self, mapping):
        self._map = mapping

    def embedding(self, texte):
        return self._map.get(texte, [0.0, 0.0, 0.0])

    def chat(self, modele, messages, temperature=None, max_tokens=None):
        return ""

    def lister_modeles(self):
        return []


def _article(titre):
    # Resume/source vides : le texte à vectoriser est exactement le titre.
    return Article(titre=titre, url=f"https://ex/{titre}", source="", resume="")


class TestSimilariteCosinus(unittest.TestCase):
    def test_identiques(self):
        self.assertAlmostEqual(similarite_cosinus([1, 0, 0], [1, 0, 0]), 1.0)

    def test_orthogonaux(self):
        self.assertAlmostEqual(similarite_cosinus([1, 0, 0], [0, 1, 0]), 0.0)

    def test_vecteur_vide(self):
        self.assertEqual(similarite_cosinus([], [1, 0, 0]), 0.0)


class TestSemantique(unittest.TestCase):
    def test_vectoriser(self):
        client = FakeEmbedding({"Politique": [1.0, 0.0, 0.0]})
        self.assertEqual(vectoriser(_article("Politique"), client), [1.0, 0.0, 0.0])

    def test_dedup(self):
        mapping = {"A": [1.0, 0.0, 0.0], "B": [1.0, 0.0, 0.0], "C": [0.0, 1.0, 0.0]}
        gardes = dedupliciter(
            [_article("A"), _article("B"), _article("C")],
            FakeEmbedding(mapping),
            seuil=0.9,
        )
        # A et B quasi identiques (cos 1.0) -> un seul conservé ; C distinct.
        self.assertEqual(len(gardes), 2)
        self.assertEqual(gardes[0].titre, "A")
        self.assertEqual(gardes[1].titre, "C")

    def test_regroupement(self):
        mapping = {"X": [1.0, 0.0, 0.0], "Y": [1.0, 0.0, 0.0], "Z": [0.0, 1.0, 0.0]}
        groupes = groupes_ordonnes(
            [_article("X"), _article("Y"), _article("Z")],
            FakeEmbedding(mapping),
            seuil=0.7,
        )
        self.assertEqual(sorted(len(g) for g in groupes), [1, 2])


if __name__ == "__main__":
    unittest.main()
