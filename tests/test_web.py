"""Tests de l'interface web (clés d'URL, accès aux données, configuration)."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Ajoute la racine du projet au PATH pour pouvoir importer le module « news_intell ».
RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from news_intell.web.config_store import ConfigStore
from news_intell.web.repository import DepotResultats, _slug


class TestSlug(unittest.TestCase):
    def test_slug_simple(self):
        self.assertEqual(_slug("Un Grand Titre !"), "un-grand-titre")

    def test_slug_accents(self):
        self.assertEqual(
            _slug("L'économie à l'ère du café"), "l-economie-a-l-ere-du-cafe"
        )


class TestConfigStore(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = ConfigStore(Path(tmp) / "config.yaml")
            dossier.sauvegarder_yaml("base_url: http://localhost:8080\ntimeout: 120\n")
            config = dossier.charger()
            self.assertEqual(config["base_url"], "http://localhost:8080")
            self.assertEqual(config["timeout"], 120)

    def test_erreur_non_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            dossier = ConfigStore(Path(tmp) / "config.yaml")
            with self.assertRaises(ValueError):
                dossier.sauvegarder_yaml("- a\n- b\n")


class TestDepotResultats(unittest.TestCase):
    def test_lister_trie(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "resultats.json"
            chemin.write_text(
                json.dumps([
                    {"titre": "Bas", "pertinence": 0.3},
                    {"titre": "Haut", "pertinence": 0.9},
                ]),
                encoding="utf-8",
            )
            depot = DepotResultats(chemin)
            self.assertEqual(depot.lister()[0]["titre"], "Haut")

    def test_get_par_cle(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "resultats.json"
            chemin.write_text(
                json.dumps([{"titre": "Un Grand Titre", "pertinence": 0.9}]),
                encoding="utf-8",
            )
            depot = DepotResultats(chemin)
            self.assertIsNotNone(depot.get_par_cle("un-grand-titre"))


if __name__ == "__main__":
    unittest.main()
