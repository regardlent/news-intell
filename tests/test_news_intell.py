"""Tests unitaires du projet news-intell.

Lancement depuis la racine du projet :
    python -m unittest discover -s tests
"""
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

from news_intell.agents.base import Agent
from news_intell.models import AnalyseArticle, Article
from news_intell.sources.rss import analyser_flux_xml
from news_intell.storage import sauvegarder_articles, sauvegarder_resultats


class TestExtraireJson(unittest.TestCase):
    """Vérifie l'extraction tolérante d'un objet JSON."""

    def test_json_simple(self):
        self.assertEqual(Agent.extraire_json('{"cle": "valeur"}'), {"cle": "valeur"})

    def test_json_bloc(self):
        texte = 'Voici le résultat :\n```json\n{"thematique": "Politique"}\n```\nFin.'
        self.assertEqual(Agent.extraire_json(texte), {"thematique": "Politique"})

    def test_json_imbrique(self):
        texte = 'Texte avant {"a": {"b": 1}} texte après'
        self.assertEqual(Agent.extraire_json(texte), {"a": {"b": 1}})

    def test_non_json(self):
        self.assertEqual(Agent.extraire_json("pas de json"), {"valeur": "pas de json"})


class TestFluxRSS(unittest.TestCase):
    """Vérifie l'analyse des flux RSS / Atom."""

    ECHANTILLON = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0"><channel><title>Test</title>
      <item>
        <title>Un titre</title>
        <link>https://example.com/article1</link>
        <description>Une description.</description>
        <pubDate>Mon, 01 Jan 2026 08:00:00 +0000</pubDate>
      </item>
      <item>
        <title>Autre titre</title>
        <link>https://example.com/article2</link>
        <description>Autre description.</description>
      </item>
    </channel></rss>"""

    def test_analyse_flux(self):
        articles = analyser_flux_xml(self.ECHANTILLON, "https://example.com", "Test")
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0].titre, "Un titre")
        self.assertEqual(articles[0].url, "https://example.com/article1")
        self.assertEqual(articles[0].source, "Test")

    def test_url_relative(self):
        echantillon = (
            '<rss version="2.0"><channel><item><link>/article</link>'
            "<title>T</title></item></channel></rss>"
        )
        articles = analyser_flux_xml(echantillon, "https://example.com", "T")
        self.assertEqual(articles[0].url, "https://example.com/article")


class TestStockage(unittest.TestCase):
    """Vérifie la persistance JSON."""

    def test_articles_round_trip(self):
        article = Article(titre="T", url="https://e.com/1", source="S", resume="R", contenu="C")
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "a.json"
            sauvegarder_articles([article], chemin)
            self.assertTrue(chemin.exists())
            donnees = json.loads(chemin.read_text(encoding="utf-8"))
            self.assertEqual(donnees[0]["titre"], "T")
            self.assertEqual(donnees[0]["source"], "S")

    def test_resultats_round_trip(self):
        article = Article(titre="T", url="https://e.com/1", source="S")
        analyse = AnalyseArticle(article=article, resume_ia="Résumé", pertinence=0.8)
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "r.json"
            sauvegarder_resultats([analyse], chemin)
            donnees = json.loads(chemin.read_text(encoding="utf-8"))
            self.assertEqual(donnees[0]["pertinence"], 0.8)
            self.assertEqual(donnees[0]["resume_ia"], "Résumé")


if __name__ == "__main__":
    unittest.main()
