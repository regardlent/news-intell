"""Classe de base des agents IA du projet news-intell.

Chaque agent a une mission précise (résumé, classification, sentiment, etc.)
et s'appuie sur un modèle LocalAI pour générer une réponse en français.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from ..client import LocalAIClient
from ..config import Config


class Agent(ABC):
    """Base commune à tous les agents IA.

    Attributs de classe :
        nom: identifiant de l'agent (ex. « resume »).
        role: description du rôle (utilisée dans les rapports).

    Attributs d'instance :
        configure: réglages (modèle, température) issus de la configuration.
    """

    nom: str = "agent"
    role: str = "Agent IA générique"

    def __init__(self, client: LocalAIClient, config: Config) -> None:
        self.client = client
        self.config = config
        self.configure = config.agents.get(self.nom)

    @property
    def modele(self) -> str:
        """Modèle LocalAI à utiliser pour cet agent (avec repli sur le défaut)."""
        if self.configure is not None:
            return self.configure.modele
        defaut = self.config.agents.get("_defaut")
        return defaut.modele if defaut else "qwen3-4b"

    @property
    def temperature(self) -> float:
        """Température d'échantillonnage pour cet agent."""
        if self.configure is not None:
            return self.configure.temperature
        defaut = self.config.agents.get("_defaut")
        return defaut.temperature if defaut else 0.2

    def generer(self, systeme: str, utilisateur: str) -> str:
        """Appelle le modèle LocalAI avec un prompt système et une demande utilisateur."""
        messages = [
            {"role": "system", "content": systeme},
            {"role": "user", "content": utilisateur},
        ]
        return self.client.chat(self.modele, messages, temperature=self.temperature)

    def json_strict(self, systeme: str, utilisateur: str) -> dict[str, Any]:
        """Demande au modèle une réponse JSON valide et la parse."""
        texte = self.generer(systeme, utilisateur)
        return self.extraire_json(texte)

    @staticmethod
    def extraire_json(texte: str) -> dict[str, Any]:
        """Extrait un objet JSON depuis une réponse contenant un bloc ```json```."""
        texte = texte.strip()
        if "```json" in texte:
            debut = texte.index("```json") + len("```json")
            fin = texte.index("```", debut)
            texte = texte[debut:fin].strip()
        try:
            return json.loads(texte)
        except json.JSONDecodeError:
            # Tentative : extraire la première accolade ouvrante à la dernière fermante.
            if "{" in texte and "}" in texte:
                sous = texte[texte.index("{"): texte.rindex("}") + 1]
                try:
                    return json.loads(sous)
                except json.JSONDecodeError:
                    return {"valeur": texte}
            return {"valeur": texte}

    @abstractmethod
    def executer(self, article: Any) -> dict[str, Any]:
        """Exécute la mission de l'agent sur un article donné."""
        raise NotImplementedError
