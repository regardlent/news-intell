"""Application web (FastAPI) : interface journalistique + administration.

Lancement :
    uvicorn news_intell.web.app:app --reload
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..client import LocalAIClient
from ..config import Config
from .config_store import ConfigStore
from .recherche import rechercher_semantique, rechercher_texte
from .repository import DepotResultats, _slug
from .taches import taches

ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
templates.env.filters["slug"] = _slug

depot = DepotResultats()
config_store = ConfigStore()

_client_cache: LocalAIClient | None = None


def _obtenir_client() -> LocalAIClient:
    """Renvoie un client LocalAI réutilisé pour la recherche sémantique."""
    global _client_cache
    if _client_cache is None:
        _client_cache = LocalAIClient(Config.charger())
    return _client_cache


def _lancer_analyse() -> str:
    """Exécute le pipeline complet (analyse) en arrière-plan."""
    config = Config.charger()
    from ..pipeline import Pipeline

    pipeline = Pipeline(config)
    resultats = pipeline.executer(format_rapport="md")
    return f"{len(resultats)} article(s) analysé(s)"


def creer_app() -> FastAPI:
    app = FastAPI(title="news-intell", version="0.1.0")
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # --- Public : interface journalistique ---
    @app.get("/", response_class=HTMLResponse)
    def accueil(request: Request):
        return templates.TemplateResponse(
            request,
            "public/index.html",
            {
                "articles": depot.lister(),
                "groupes": depot.groupes(),
                "sources": depot.sources(),
                "thematiques": depot.thematiques(),
            },
        )

    @app.get("/article/{cle}", response_class=HTMLResponse)
    def article(request: Request, cle: str):
        donnees = depot.get_par_cle(cle)
        if donnees is None:
            return templates.TemplateResponse(
                request, "public/introuvable.html", {"request": request}, status_code=404
            )
        return templates.TemplateResponse(
            request, "public/article.html", {"a": donnees}
        )

    @app.get("/recherche", response_class=HTMLResponse)
    def recherche(request: Request, q: str = "", mode: str = "texte"):
        resultats = depot.lister()
        if mode == "semantique" and q:
            resultats = rechercher_semantique(resultats, q, _obtenir_client())
        else:
            resultats = rechercher_texte(resultats, q)
        return templates.TemplateResponse(
            request,
            "public/recherche.html",
            {"q": q, "mode": mode, "articles": resultats},
        )

    # --- API JSON ---
    @app.get("/api/articles")
    def api_articles():
        return JSONResponse(depot.lister())

    @app.get("/api/recherche")
    def api_recherche(q: str = "", mode: str = "texte"):
        resultats = depot.lister()
        if mode == "semantique" and q:
            resultats = rechercher_semantique(resultats, q, _obtenir_client(), top_n=20)
        else:
            resultats = rechercher_texte(resultats, q)
        return JSONResponse(resultats)

    @app.get("/api/article/{cle}")
    def api_article(cle: str):
        donnees = depot.get_par_cle(cle)
        if donnees is None:
            return JSONResponse({"erreur": "introuvable"}, status_code=404)
        return JSONResponse(donnees)

    # --- Administration ---
    @app.get("/admin", response_class=HTMLResponse)
    def admin_index(request: Request):
        config = Config.charger()
        return templates.TemplateResponse(
            request,
            "admin/index.html",
            {
                "nb_articles": len(depot.lister()),
                "sources": config.sources,
                "nb_sources": len(config.sources),
                "taches": dict(taches._taches),
            },
        )

    @app.get("/admin/config", response_class=HTMLResponse)
    def admin_config(request: Request):
        return templates.TemplateResponse(
            request,
            "admin/config.html",
            {"texte": config_store.en_yaml()},
        )

    @app.post("/admin/config")
    async def admin_config_sauver(request: Request):
        texte = (await request.body()).decode("utf-8")
        try:
            config_store.sauvegarder_yaml(texte)
        except ValueError as exc:
            return JSONResponse({"ok": False, "erreur": str(exc)}, status_code=400)
        return JSONResponse({"ok": True})

    @app.post("/admin/analyser")
    def admin_analyser():
        identifiant = taches.lancer(_lancer_analyse)
        return JSONResponse({"id": identifiant, "statut": "en_cours"})

    @app.get("/admin/taches/{identifiant}")
    def admin_tache(identifiant: str):
        return JSONResponse(taches.statut(identifiant) or {"statut": "inconnu", "resultat": ""})

    @app.get("/admin/actualiser")
    def admin_actualiser():
        return RedirectResponse("/admin", status_code=303)

    return app


app = creer_app()
