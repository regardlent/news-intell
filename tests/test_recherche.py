"""Tests de la recherche (texte + sémantique)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Ajoute la racine du projet au PATH pour pouvoir importer le module « news_intell ».
RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from news_intell.web.recherche import rechercher_semantique, rechercher_texte


class FakeClientRerank:
    """Client LocalAI simulé : le reranker renvoie des scores par index."""

    def reranker(self, requete, documents):
        return [0.5, 0.9, 0.1]

    def embedding(self, texte):
        return [1.0, 0.0, 0.0]


class FakeClientErreur:
    """Client LocalAI simulé : tous les appels échouent."""

    def reranker(self, requete, documents):
        raise RuntimeError("indisponible")

    def embedding(self, texte):
        raise RuntimeError("indisponible")


ARTICLES = [
    {"titre": "A", "thematique": "Politique", "source": "Le Monde", "mot_cle": ["a"]},
    {"titre": "B", "thematique": "Économie", "source": "France Info", "mot_cle": ["b"]},
    {"titre": "C", "thematique": "Sport", "source": "L'Équipe", "mot_cle": ["c"]},
]


class TestRechercheTexte(unittest.TestCase):
    def test_filtre_par_champ(self):
        self.assertEqual(len(rechercher_texte(ARTICLES, "économie")), 1)

    def test_sans_requete(self):
        self.assertEqual(rechercher_texte(ARTICLES, ""), ARTICLES)


class TestRechercheSemantique(unittest.TestCase):
    def test_reranker_ordonne(self):
        resultat = rechercher_semantique(ARTICLES, "budget", FakeClientRerank())
        self.assertEqual(resultat[0]["titre"], "B")  # score 0.9 en premier
        self.assertEqual(resultat[2]["titre"], "C")  # score 0.1 en dernier

    def test_repli_texte_sur_erreur(self):
        resultat = rechercher_semantique(ARTICLES, "économie", FakeClientErreur())
        self.assertEqual(len(resultat), 1)
        self.assertEqual(resultat[0]["thematique"], "Économie")


if __name__ == "__main__":
    unittest.main()
