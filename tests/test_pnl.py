"""Tests du système PNL (analyse comportementale) et du cœur (analyste + travailleurs)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Ajoute la racine du projet au PATH pour pouvoir importer le module « news_intell ».
RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from news_intell.agents.pnl.noir import AgentPNLNoir
from news_intell.agents.pnl.team import EquipePNL
from news_intell.config import Config
from news_intell.core.analyst import Analyste
from news_intell.core.workers import Travailleur
from news_intell.models import AnalyseArticle, Article

JSON_NEURO = '{"neuro": [{"technique": "recadrage", "exemple": "…", "description": "…"}]}'
JSON_NOIR = (
    '{"noir": [{"technique": "appel à la peur", "exemple": "…", '
    '"indice_manipulation": 0.7}], "score_manipulation": 1.4, '
    '"boutons_chauds": ["peur", "urgence"], "niveau_manipulation": "élevé"}'
)
NOTE = "Note d'analyse rédigée par l'analyste."
FULL = (
    '{"resume_ia": "Résumé", "thematique": "Politique", "categories": ["Économie"], '
    '"sentiment": "neutre", "score_sentiment": 0.0, '
    '"entites": {"personnes": [], "organisations": [], "lieux": []}, '
    '"pertinence": 0.7, "mot_cle": ["test"], '
    '"neuro": [{"technique": "recadrage"}], "noir": [{"technique": "peur"}], '
    '"score_manipulation": 0.3, "niveau_manipulation": "faible", '
    '"boutons_chauds": ["peur"]}'
)


class FakeClient:
    """Client LocalAI simulé : renvoie les réponses fournies dans l'ordre."""

    def __init__(self, reponses):
        self._reponses = list(reponses)

    def chat(self, modele, messages, temperature=None, max_tokens=None):
        if self._reponses:
            return self._reponses.pop(0)
        return ""

    def embedding(self, texte):
        return [0.0]

    def lister_modeles(self):
        return []


class ClientQuiEchoue:
    """Client LocalAI simulé dont chaque appel échoue."""

    def chat(self, modele, messages, temperature=None, max_tokens=None):
        raise RuntimeError("échec simulé")

    def embedding(self, texte):
        return [0.0]

    def lister_modeles(self):
        return []


def _config():
    return Config()


def _article():
    return Article(titre="Titre", url="https://ex.1", source="S", contenu="Contenu...")


class TestEquipePNL(unittest.TestCase):
    def test_analyse_agregee(self):
        client = FakeClient([JSON_NEURO, JSON_NOIR])
        pnl = EquipePNL(client, _config()).analyser(_article())
        self.assertEqual(len(pnl.neuro), 1)
        self.assertEqual(len(pnl.noir), 1)
        self.assertEqual(pnl.niveau_manipulation, "élevé")
        self.assertEqual(pnl.score_manipulation, 1.0)  # plafonné à 1.0
        self.assertIn("peur", pnl.boutons_chauds)

    def test_erreurs_agent(self):
        pnl = EquipePNL(ClientQuiEchoue(), _config()).analyser(_article())
        self.assertTrue(pnl.erreurs)  # les deux agents échouent et sont enregistrés
        self.assertEqual(pnl.score_manipulation, 0.0)
        self.assertEqual(pnl.niveau_manipulation, "faible")


class TestAgentPNLNoir(unittest.TestCase):
    def test_score_plafonne(self):
        agent = AgentPNLNoir(FakeClient([JSON_NOIR]), _config())
        resultat = agent.executer(_article())
        self.assertEqual(resultat["score_manipulation"], 1.0)
        self.assertEqual(resultat["niveau_manipulation"], "élevé")


class TestAnalyste(unittest.TestCase):
    def test_redige(self):
        analyste = Analyste(FakeClient([NOTE]), _config())
        article = _article()
        analyse = AnalyseArticle(article=article, thematique="Politique", pertinence=0.8)
        texte = analyste.rediger(article, analyse, None)
        self.assertEqual(texte, NOTE)


class TestTravailleur(unittest.TestCase):
    def test_traitement_complet(self):
        # 5 agents de base + 2 agents PNL + 1 analyste = 8 appels.
        reps = [FULL, FULL, FULL, FULL, FULL, FULL, FULL, FULL]
        analyse = Travailleur(FakeClient(reps), _config()).traiter(_article())
        self.assertEqual(analyse.thematique, "Politique")
        self.assertEqual(analyse.pertinence, 0.7)
        self.assertIsNotNone(analyse.pnl)
        self.assertEqual(analyse.pnl.score_manipulation, 0.3)
        self.assertEqual(analyse.pnl.niveau_manipulation, "faible")
        self.assertEqual(analyse.note_analyste, FULL)


if __name__ == "__main__":
    unittest.main()
