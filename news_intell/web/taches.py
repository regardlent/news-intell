"""Exécution d'analyses en arrière-plan depuis l'interface d'administration."""
from __future__ import annotations

import threading
import uuid
from typing import Any, Callable


class GestionnaireTaches:
    """Suivi des analyses lancées en arrière-plan."""

    def __init__(self) -> None:
        self._taches: dict[str, dict[str, str]] = {}
        self._verrou = threading.Lock()

    def lancer(self, fonction: Callable[..., Any], *args: Any, **kwargs: Any) -> str:
        identifiant = uuid.uuid4().hex[:12]
        with self._verrou:
            self._taches[identifiant] = {"statut": "en_cours", "resultat": ""}
        thread = threading.Thread(
            target=self._executer,
            args=(identifiant, fonction, args, kwargs),
            daemon=True,
        )
        thread.start()
        return identifiant

    def _executer(
        self,
        identifiant: str,
        fonction: Callable[..., Any],
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> None:
        try:
            resultat = fonction(*args, **kwargs)
            self._taches[identifiant] = {"statut": "termine", "resultat": str(resultat)}
        except Exception as exc:  # noqa: BLE001
            self._taches[identifiant] = {"statut": "erreur", "resultat": str(exc)}

    def statut(self, identifiant: str) -> dict[str, str] | None:
        with self._verrou:
            return self._taches.get(identifiant)


taches = GestionnaireTaches()
