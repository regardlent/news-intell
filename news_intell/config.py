"""Configuration du projet news-intell.

Charge la configuration depuis `config/config.yaml` ainsi que les variables
d'environnement depuis un fichier `.env` (ou l'environnement réel).
L'ensemble est documenté en français.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Racine du projet (deux niveaux au-dessus de ce fichier : news_intell/config.py).
PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"
ENV_PATH = PROJECT_ROOT / ".env"


def _charger_env(chemin: Path) -> None:
    """Charge un fichier `.env` minimal dans l'environnement (sans dépendance externe)."""
    if not chemin.exists():
        return
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, valeur = ligne.split("=", 1)
        os.environ.setdefault(cle.strip(), valeur.strip().strip('"').strip("'"))


@dataclass
class AgentConfig:
    """Configuration d'un agent IA (modèle + réglages)."""

    modele: str = "qwen3-4b"
    temperature: float = 0.2

    @classmethod
    def depuis_dict(cls, donnees: dict[str, Any]) -> "AgentConfig":
        return cls(
            modele=donnees.get("modele", "qwen3-4b"),
            temperature=float(donnees.get("temperature", 0.2)),
        )


@dataclass
class Config:
    """Configuration globale de l'application."""

    base_url: str = "http://localhost:8080"
    api_key: str = ""
    modele_embedding: str = "hal-qwen3-embedding-0.6b"
    modele_reranker: str = "jina-reranker-v1-base-en"
    timeout: float = 60.0
    langue: str = "fr"
    agents: dict[str, AgentConfig] = field(default_factory=dict)
    sources: list[dict[str, Any]] = field(default_factory=list)
    seuils: dict[str, float] = field(default_factory=dict)
    pnl_active: bool = True
    nb_workers: int = 1

    @classmethod
    def charger(cls) -> "Config":
        """Construit la configuration depuis le fichier YAML et l'environnement."""
        _charger_env(ENV_PATH)

        donnees: dict[str, Any] = {}
        if CONFIG_PATH.exists():
            donnees = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}

        agents = {
            nom: AgentConfig.depuis_dict(v)
            for nom, v in (donnees.get("agents") or {}).items()
        }

        pnl_section = donnees.get("pnl", {})
        pnl_active = True
        if isinstance(pnl_section, dict):
            pnl_active = bool(pnl_section.get("active", True))

        return cls(
            base_url=os.environ.get(
                "LOCALAI_BASE_URL", donnees.get("base_url", "http://localhost:8080")
            ),
            api_key=os.environ.get("LOCALAI_API_KEY", donnees.get("api_key", "")),
            modele_embedding=donnees.get(
                "modele_embedding", "hal-qwen3-embedding-0.6b"
            ),
            modele_reranker=donnees.get("modele_reranker", "jina-reranker-v1-base-en"),
            timeout=float(donnees.get("timeout", 60.0)),
            langue=donnees.get("langue", "fr"),
            agents=agents,
            sources=donnees.get("sources", []),
            seuils=donnees.get("seuils", {}),
            pnl_active=pnl_active,
            nb_workers=int(donnees.get("nb_workers", 1)),
        )
