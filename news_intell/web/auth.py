"""Authentification simple du panneau d'administration."""
from __future__ import annotations

import os
import secrets

from fastapi import Request

from ..config import Config

SESSION_ADMIN = "admin"
SECRET_DEFAUT = "news-intell-secret-dev"


def mot_de_passe_admin() -> str:
    """Mot de passe admin (env ADMIN_PASSWORD ou config.admin.mot_de_passe)."""
    env = os.environ.get("ADMIN_PASSWORD")
    if env:
        return env
    config = Config.charger()
    admin = config.admin or {}
    return str(admin.get("mot_de_passe", "")) if isinstance(admin, dict) else ""


def secret_session() -> str:
    """Secret de signature de session (env SESSION_SECRET, sinon valeur de dev)."""
    return os.environ.get("SESSION_SECRET", SECRET_DEFAUT)


def verifier_mot_de_passe(entree: str) -> bool:
    """Compare (de façon sûre) le mot de passe fourni au mot de passe attendu."""
    attendu = mot_de_passe_admin()
    if not attendu:
        return False
    return secrets.compare_digest(entree, attendu)


def est_authentifie(request: Request) -> bool:
    """Vérifie que la session indique un administrateur connecté."""
    return bool(request.session.get(SESSION_ADMIN))


def marquer_authentifie(request: Request) -> None:
    """Marque la session comme administrateur connecté."""
    request.session[SESSION_ADMIN] = True


def deconnecter(request: Request) -> None:
    """Efface la session d'administration."""
    request.session.clear()
