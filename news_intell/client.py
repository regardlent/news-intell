"""Client HTTP compatible OpenAI vers un serveur LocalAI.

Fournit `chat` (complétion de dialogue) et `embedding` (vecteurs).
Toutes les réponses sont analysées en français via les prompts des agents.
"""
from __future__ import annotations

from typing import Any

import requests

from .config import Config


class LocalAIClient:
    """Client minimaliste pour l'API OpenAI-compatible de LocalAI."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._base = config.base_url.rstrip("/")
        self._session = requests.Session()
        self._headers = {"Content-Type": "application/json"}
        if config.api_key:
            self._headers["Authorization"] = f"Bearer {config.api_key}"

    @property
    def base_url(self) -> str:
        return self._base

    def chat(
        self,
        modele: str,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Envoie un dialogue de chat et renvoie la réponse textuelle du modèle."""
        payload: dict[str, Any] = {
            "model": modele,
            "messages": messages,
            "temperature": temperature if temperature is not None else 0.2,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        try:
            reponse = self._session.post(
                f"{self._base}/v1/chat/completions",
                headers=self._headers,
                json=payload,
                timeout=self._config.timeout,
            )
            reponse.raise_for_status()
            donnees = reponse.json()
            return donnees["choices"][0]["message"]["content"].strip()
        except requests.RequestException as exc:
            raise RuntimeError(f"Erreur d'appel LocalAI (chat) : {exc}") from exc

    def embedding(self, texte: str) -> list[float]:
        """Calcule le vecteur d'embedding d'un texte."""
        payload = {"model": self._config.modele_embedding, "input": texte}
        try:
            reponse = self._session.post(
                f"{self._base}/v1/embeddings",
                headers=self._headers,
                json=payload,
                timeout=self._config.timeout,
            )
            reponse.raise_for_status()
            donnees = reponse.json()
            return donnees["data"][0]["embedding"]
        except requests.RequestException as exc:
            raise RuntimeError(f"Erreur d'appel LocalAI (embedding) : {exc}") from exc

    def lister_modeles(self) -> list[dict[str, Any]]:
        """Liste les modèles chargés sur le serveur LocalAI."""
        try:
            reponse = self._session.get(
                f"{self._base}/v1/models",
                headers=self._headers,
                timeout=self._config.timeout,
            )
            reponse.raise_for_status()
            return list(reponse.json().get("data", []))
        except requests.RequestException as exc:
            raise RuntimeError(f"Erreur d'appel LocalAI (modèles) : {exc}") from exc

    def modele_disponible(self, modele: str) -> bool:
        """Vérifie si un modèle est chargé sur le serveur LocalAI."""
        return any(m.get("id") == modele for m in self.lister_modeles())
