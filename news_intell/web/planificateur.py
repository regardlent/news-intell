"""Planification périodique des analyses depuis l'interface d'administration."""
from __future__ import annotations

import threading
import time
from typing import Callable, Optional


class Planificateur:
    """Lance une analyse à intervalle régulier (en arrière-plan)."""

    def __init__(self) -> None:
        self._arret = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._intervalle: int = 0

    def demarrer(self, intervalle_minutes: int, fonction: Callable[[], str]) -> int:
        """Démarre (ou redémarre) la planification. Renvoie l'intervalle."""
        if intervalle_minutes < 5:
            raise ValueError("L'intervalle doit être d'au moins 5 minutes.")
        self.arreter()
        self._intervalle = intervalle_minutes
        self._arret.clear()
        self._thread = threading.Thread(
            target=self._boucle, args=(fonction,), daemon=True
        )
        self._thread.start()
        return self._intervalle

    def _boucle(self, fonction: Callable[[], str]) -> None:
        while not self._arret.is_set():
            time.sleep(60 * self._intervalle)
            if self._arret.is_set():
                break
            try:
                fonction()
            except Exception:  # noqa: BLE001
                continue

    def arreter(self) -> None:
        """Arrête la planification."""
        self._arret.set()

    def actif(self) -> bool:
        """Indique si une planification est en cours."""
        return bool(self._thread and self._thread.is_alive())

    @property
    def intervalle(self) -> int:
        return self._intervalle


planificateur = Planificateur()
