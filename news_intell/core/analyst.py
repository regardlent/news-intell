"""Agent analyste : rédige la note d'analyse comportementale (par écrit)."""
from __future__ import annotations

from ..client import LocalAIClient
from ..config import Config
from ..models import AnalyseArticle, AnalysePNL, Article

SYSTEME_NOTE = (
    "Tu es un analyste éditorial et un veilleur cultivé, expert de l'actualité "
    "francophone. Rédige une note d'analyse concise, en français, à partir de "
    "l'article et des analyses fournies (thématique, sentiment, entités, "
    "pertinence et lecture comportementale PNL). La note doit couvrir : 1) "
    "l'essentiel de l'article, 2) le ton et le traitement éditorial, 3) la lecture "
    "comportementale (techniques d'influence détectées, niveau de manipulation), "
    "4) les signaux ou tendances utiles pour un lecteur. Rédige environ 60 à 90 "
    "mots en paragraphes courts, sans mention « Note ». Sois synthétique, nuancé "
    "et direct."
)


class Analyste:
    """Produit une note d'analyse écrite et structurée en français."""

    nom = "analyste"
    role = "Rédaction de la note d'analyse comportementale"
    max_tokens: int = 180

    def __init__(self, client: LocalAIClient, config: Config) -> None:
        self.client = client
        self.config = config
        self.configure = config.agents.get(self.nom)

    @property
    def modele(self) -> str:
        """Modèle LocalAI à utiliser (avec repli sur le défaut)."""
        if self.configure is not None:
            return self.configure.modele
        defaut = self.config.agents.get("_defaut")
        return defaut.modele if defaut else "qwen3-4b"

    @property
    def temperature(self) -> float:
        """Température d'échantillonnage."""
        if self.configure is not None:
            return self.configure.temperature
        defaut = self.config.agents.get("_defaut")
        return defaut.temperature if defaut else 0.3

    def rediger(
        self,
        article: Article,
        analyse: AnalyseArticle,
        pnl: AnalysePNL | None,
    ) -> str:
        """Rédige et renvoie la note d'analyse comportementale."""
        utilisateur = self._construire_prompt(article, analyse, pnl)
        messages = [
            {"role": "system", "content": SYSTEME_NOTE},
            {"role": "user", "content": utilisateur},
        ]
        return self.client.chat(
            self.modele,
            messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def _construire_prompt(
        self,
        article: Article,
        analyse: AnalyseArticle,
        pnl: AnalysePNL | None,
    ) -> str:
        categories = ", ".join(analyse.categories) or "n/a"
        lignes = [
            f"Titre : {article.titre}",
            f"Source : {article.source}",
            f"Thématique : {analyse.thematique or 'n/a'}",
            f"Catégories : {categories}",
            f"Sentiment : {analyse.sentiment} ({analyse.score_sentiment:+.2f})",
            f"Pertinence : {analyse.pertinence:.2f}",
        ]
        if analyse.resume_ia:
            lignes.append(f"Résumé : {analyse.resume_ia}")
        contenu = article.contenu or article.resume or article.titre
        return "\n".join(lignes) + (
            f"\n\nLecture comportementale (PNL) :\n{self._decrire_pnl(pnl)}\n\n"
            f"Contenu de l'article :\n{contenu[:6000]}"
        )

    @staticmethod
    def _decrire_pnl(pnl: AnalysePNL | None) -> str:
        """Résume l'analyse PNL pour l'inclure dans le prompt de rédaction."""
        if pnl is None:
            return "Non analysée."
        neuro = ", ".join(str(n.get("technique", "")) for n in pnl.neuro) or "aucune"
        noir = ", ".join(str(n.get("technique", "")) for n in pnl.noir) or "aucune"
        boutons = ", ".join(pnl.boutons_chauds) or "aucun"
        return (
            f"Score de manipulation : {pnl.score_manipulation:.2f} "
            f"(niveau {pnl.niveau_manipulation}). "
            f"Techniques constructives : {neuro}. "
            f"Techniques de manipulation : {noir}. "
            f"Déclencheurs émotionnels : {boutons}."
        )
