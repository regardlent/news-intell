"""Tests des statistiques du tableau de bord et de la planification."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Ajoute la racine du projet au PATH pour pouvoir importer le module « news_intell ».
RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from news_intell.web.planificateur import Planificateur
from news_intell.web.statistiques import calculer_statistiques

ARTICLES = [
    {
        "titre": "A",
        "source": "Le Monde",
        "thematique": "Politique",
        "sentiment": "neutre",
        "mot_cle": ["budget", "gouvernement"],
        "pertinence": 0.8,
    },
    {
        "titre": "B",
        "source": "France Info",
        "thematique": "Politique",
        "sentiment": "negatif",
        "mot_cle": ["budget", "crise"],
        "pertinence": 0.6,
    },
    {
        "titre": "C",
        "source": "L'Équipe",
        "thematique": "Sport",
        "sentiment": "positif",
        "mot_cle": ["foot"],
        "pertinence": 0.4,
    },
]


class TestStatistiques(unittest.TestCase):
    def test_indicateurs(self):
        stats = calculer_statistiques(ARTICLES)
        self.assertEqual(len(stats["par_source"]), 3)
        self.assertEqual(stats["par_theme"][0][0], "Politique")
        self.assertEqual(stats["par_theme"][0][1], 2)
        # « budget » apparaît deux fois.
        self.assertEqual(stats["mots_courants"][0][0], "budget")
        self.assertAlmostEqual(stats["moyenne_pertinence"], round((0.8 + 0.6 + 0.4) / 3, 2))

    def test_vide(self):
        stats = calculer_statistiques([])
        self.assertEqual(stats["par_source"], [])
        self.assertEqual(stats["moyenne_pertinence"], 0.0)


class TestPlanificateur(unittest.TestCase):
    def test_intervalle_minimum(self):
        planificateur = Planificateur()
        with self.assertRaises(ValueError):
            planificateur.demarrer(1, lambda: "ok")

    def test_arrete(self):
        planificateur = Planificateur()
        planificateur.demarrer(60, lambda: "ok")
        self.assertTrue(planificateur.actif())
        planificateur.arreter()
        # l'état 'actif' dépend du thread ; on s'assure que l'arrêt ne lève pas.
        planificateur.arreter()


if __name__ == "__main__":
    unittest.main()
