"""Accès en lecture/écriture à la configuration depuis l'interface d'administration."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ..config import PROJECT_ROOT

CHEMIN_CONFIG = PROJECT_ROOT / "config" / "config.yaml"


class ConfigStore:
    """Lit et modifie la configuration YAML du projet."""

    def __init__(self, chemin: Path = CHEMIN_CONFIG) -> None:
        self.chemin = Path(chemin)

    def charger(self) -> dict[str, Any]:
        """Renvoie la configuration sous forme de dictionnaire."""
        if not self.chemin.exists():
            return {}
        donnees = yaml.safe_load(self.chemin.read_text(encoding="utf-8"))
        return donnees if isinstance(donnees, dict) else {}

    def en_yaml(self) -> str:
        """Renvoie la configuration au format YAML (pour l'édition)."""
        return yaml.safe_dump(
            self.charger(), allow_unicode=True, sort_keys=False, default_flow_style=False
        )

    def sauvegarder_yaml(self, texte: str) -> None:
        """Enregistre une configuration YAML (les commentaires ne sont pas conservés)."""
        donnees = yaml.safe_load(texte)
        if not isinstance(donnees, dict):
            raise ValueError("La configuration doit être un objet YAML (mapping).")
        self.chemin.write_text(
            yaml.safe_dump(donnees, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def sauvegarder(self, donnees: dict[str, Any]) -> None:
        """Écrit une configuration depuis un dictionnaire."""
        self.chemin.write_text(
            yaml.safe_dump(donnees, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
