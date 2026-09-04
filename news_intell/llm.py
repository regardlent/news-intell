"""Moteur de modèle de langage pluggable.

Permet d'utiliser indifféremment :
- `localai` : un serveur LocalAI (API compatible OpenAI) via `LocalAIClient` ;
- `personnalise` : un **modèle local personnalisé** (ex. GGUF) chargé directement
  en mémoire, sans passer par une API HTTP.

Le backend s'active via `config.backend`.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any

from .client import LocalAIClient
from .config import Config


class InterfaceLLM(ABC):
    """Interface commune des moteurs de modèle de langage."""

    @abstractmethod
    def chat(
        self,
        modele: str,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Génère une réponse de dialogue."""

    @abstractmethod
    def embedding(self, texte: str) -> list[float]:
        """Calcule un vecteur d'embedding."""

    @abstractmethod
    def lister_modeles(self) -> list[dict[str, Any]]:
        """Liste les modèles disponibles."""

    def reranker(self, requete: str, documents: list[str]) -> list[float]:
        """Classe des documents par pertinence (repli : non supporté)."""
        raise NotImplementedError("Reranker non supporté par ce backend.")


class ModelePersonnalise(InterfaceLLM):
    """Modèle local « personnalisé » chargé directement en mémoire.

    Nécessite `llama-cpp-python` (ou un chargeur équivalent) et un fichier de
    modèle GGUF fourni dans la configuration (`modele_personnalise.chemin`).
    Ce backend **n'utilise aucune API HTTP** (LocalAI non requis).
    """

    def __init__(self, config: Config) -> None:
        try:
            from llama_cpp import Llama  # noqa: WPS433
        except ImportError as exc:  # noqa: BLE001
            raise RuntimeError(
                "Backend 'personnalise' : installez « llama-cpp-python » et fournissez "
                "un modèle GGUF (config.modele_personnalise.chemin)."
            ) from exc

        reglages = config.modele_personnalise or {}
        reglages_llm = config.llm or {}
        chemin = reglages.get("chemin", "")
        if not chemin:
            raise RuntimeError("modele_personnalise.chemin est requis (chemin vers un .gguf).")

        n_ctx = int(reglages_llm.get("contexte", 8192))
        n_threads = int(reglages_llm.get("nb_threads", os.cpu_count() or 4))
        n_gpu = int(reglages_llm.get("gpu_couches", 0))
        try:
            self._llm = Llama(
                model_path=str(chemin),
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_gpu_layers=n_gpu,
            )
        except Exception:  # noqa: BLE001 — repli CPU si l'offchargement GPU échoue
            self._llm = Llama(
                model_path=str(chemin),
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_gpu_layers=0,
            )
        self._modele = reglages.get("nom", str(chemin))

    @staticmethod
    def _prompt(messages: list[dict[str, str]]) -> str:
        """Transforme des messages (rôle/contenu) en un prompt texte simple."""
        lignes: list[str] = []
        for message in messages:
            contenu = message.get("content", "")
            role = message.get("role", "user")
            if role == "system":
                lignes.append(f"[INST] {contenu} [/INST]")
            elif role == "user":
                lignes.append(f"[INST] {contenu} [/INST]")
            else:
                lignes.append(contenu)
        return "\n".join(lignes)

    def chat(
        self,
        modele: str,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        sortie = self._llm(
            self._prompt(messages),
            max_tokens=max_tokens or 256,
            temperature=temperature if temperature is not None else 0.2,
            echo=False,
        )
        return sortie["choices"][0]["text"].strip()

    def embedding(self, texte: str) -> list[float]:
        raise NotImplementedError("Embeddings non pris en charge par ce backend.")

    def lister_modeles(self) -> list[dict[str, Any]]:
        return [{"id": self._modele}]


def creer_llm(config: Config) -> InterfaceLLM:
    """Renvoie le moteur de modèle correspondant au backend configuré.

    - `localai` → `LocalAIClient` (serveur LocalAI, API compatible OpenAI).
    - `personnalise` → `ModelePersonnalise` (modèle local chargé en mémoire).
    """
    if getattr(config, "backend", "localai") == "personnalise":
        return ModelePersonnalise(config)
    return LocalAIClient(config)
