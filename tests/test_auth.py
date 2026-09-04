"""Tests de l'authentification de l'administration."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

# Ajoute la racine du projet au PATH pour pouvoir importer le module « news_intell ».
RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from news_intell.web import auth


class TestAuth(unittest.TestCase):
    def test_mot_de_passe_env(self):
        os.environ["ADMIN_PASSWORD"] = "secret123"
        try:
            self.assertTrue(auth.verifier_mot_de_passe("secret123"))
            self.assertFalse(auth.verifier_mot_de_passe("autre"))
        finally:
            os.environ.pop("ADMIN_PASSWORD", None)

    def test_mot_de_passe_incorrect(self):
        os.environ.pop("ADMIN_PASSWORD", None)
        self.assertFalse(auth.verifier_mot_de_passe("mauvais"))

    def test_secret_session(self):
        self.assertTrue(auth.secret_session())


if __name__ == "__main__":
    unittest.main()
