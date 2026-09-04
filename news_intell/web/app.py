"""Application web (FastAPI) : interface journalistique + administration.

Lancement :
    uvicorn news_intell.web.app:app --reload
"""
from __future__ import annotations

import csv
import io
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..config import Config
from ..llm import InterfaceLLM, creer_llm
from .config_store import ConfigStore
from .planificateur import planificateur
from .recherche import rechercher_semantique, rechercher_texte
from .repository import DepotResultats, _slug
from .statistiques import calculer_statistiques
from .taches import taches

ROOT = Path(__file__).resolve().parent
TEMPLATE_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
templates.env.filters["slug"] = _slug

depot = DepotResultats()
config_store = ConfigStore()

_client_cache: InterfaceLLM | None = None


def _obtenir_client() -> InterfaceLLM:
    """Renvoie le moteur de modèle réutilisé pour la recherche sémantique."""
    global _client_cache
    if _client_cache is None:
        _client_cache = creer_llm(Config.charger())
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

    origines = [
        o.strip()
        for o in os.environ.get("CORS_ORIGINS", "*").split(",")
        if o.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origines,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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

    @app.get("/api/export.csv")
    def api_export():
        donnees = depot.lister()
        boucle = io.StringIO()
        ecrivain = csv.writer(boucle, delimiter=";")
        ecrivain.writerow([
            "titre", "source", "thematique", "sentiment", "pertinence",
            "groupe", "url", "note_analyste",
        ])
        for r in donnees:
            ecrivain.writerow([
                r.get("titre", ""),
                r.get("source", ""),
                r.get("thematique", ""),
                r.get("sentiment", ""),
                r.get("pertinence", ""),
                r.get("groupe", ""),
                r.get("url", ""),
                r.get("note_analyste", ""),
            ])
        return Response(content=boucle.getvalue(), media_type="text/csv; charset=utf-8")

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
                "stats": calculer_statistiques(depot.lister()),
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

    @app.post("/admin/planifier")
    def admin_planifier(intervalle: int = 60):
        try:
            planificateur.demarrer(intervalle, _lancer_analyse)
        except ValueError as exc:
            return JSONResponse({"ok": False, "erreur": str(exc)}, status_code=400)
        return JSONResponse({"ok": True, "intervalle": intervalle, "statut": "actif"})

    @app.get("/admin/planification")
    def admin_planification():
        return JSONResponse({
            "actif": planificateur.actif(),
            "intervalle": planificateur.intervalle,
        })

    return app


app = creer_app()
