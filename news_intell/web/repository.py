"""Accès aux données d'analyse pour l'interface web."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any


def _slug(texte: str) -> str:
    """Normalise un texte en clé d'URL (minuscules, tirets, sans accents)."""
    normalise = unicodedata.normalize("NFD", texte or "")
    ascii_ = normalise.encode("ascii", "ignore").decode("ascii")
    ascii_ = ascii_.lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_).strip("-")


class DepotResultats:
    """Fournit les analyses enregistrées (data/resultats.json)."""

    def __init__(self, chemin: Path = Path("data") / "resultats.json") -> None:
        self.chemin = Path(chemin)

    def charger(self) -> list[dict[str, Any]]:
        if not self.chemin.exists():
            return []
        donnees = json.loads(self.chemin.read_text(encoding="utf-8"))
        return donnees if isinstance(donnees, list) else []

    def lister(self) -> list[dict[str, Any]]:
        """Articles triés par pertinence décroissante."""
        return sorted(
            self.charger(), key=lambda r: r.get("pertinence", 0.0), reverse=True
        )

    def sources(self) -> list[str]:
        vues = sorted({r.get("source") for r in self.charger() if r.get("source")})
        return vues

    def thematiques(self) -> list[str]:
        vues = sorted({r.get("thematique") for r in self.charger() if r.get("thematique")})
        return vues

    def groupes(self) -> dict[int, list[dict[str, Any]]]:
        """Regroupe les analyses par identifiant de groupe (sujet)."""
        regroupement: dict[int, list[dict[str, Any]]] = {}
        for r in self.lister():
            regroupement.setdefault(int(r.get("groupe", 0)), []).append(r)
        return regroupement

    def get_par_cle(self, cle: str) -> dict[str, Any] | None:
        """Retrouve une analyse par son titre (ou sa version slugifiée)."""
        for r in self.lister():
            if _slug(r.get("titre", "")) == cle:
                return r
        return None
