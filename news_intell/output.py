"""Génération de rapports d'analyse en français (Markdown / CSV / HTML)."""
from __future__ import annotations

import csv
from html import escape
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import AnalyseArticle


def _tri(resultats: list["AnalyseArticle"]) -> list["AnalyseArticle"]:
    """Trie les résultats par pertinence décroissante."""
    return sorted(resultats, key=lambda r: r.pertinence, reverse=True)


def generer_rapport(
    resultats: list["AnalyseArticle"],
    dossier: Path,
    format: str = "md",
) -> Path:
    """Génère un rapport dans le format demandé et renvoie son chemin."""
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    if format == "csv":
        chemin = dossier / "rapport.csv"
        _rapport_csv(resultats, chemin)
    elif format == "html":
        chemin = dossier / "rapport.html"
        _rapport_html(resultats, chemin)
    else:
        chemin = dossier / "rapport.md"
        _rapport_markdown(resultats, chemin)
    return chemin


def _rapport_markdown(resultats: list["AnalyseArticle"], chemin: Path) -> None:
    lignes = ["# Rapport d'analyse de l'actualité\n"]
    for r in _tri(resultats):
        lignes.append(f"## {r.article.titre}")
        lignes.append(f"- **Source** : {r.article.source}")
        if r.article.date_publication:
            lignes.append(f"- **Date** : {r.article.date_publication}")
        lignes.append(f"- **Thématique** : {r.thematique or 'n/a'}")
        categories = ", ".join(r.categories) if r.categories else "n/a"
        lignes.append(f"- **Catégories** : {categories}")
        lignes.append(f"- **Sentiment** : {r.sentiment} ({r.score_sentiment:+.2f})")
        lignes.append(f"- **Pertinence** : {r.pertinence:.2f}")
        if r.pnl is not None:
            lignes.append(
                f"- **Manipulation (PNL)** : {r.pnl.score_manipulation:.2f} "
                f"({r.pnl.niveau_manipulation})"
            )
            boutons = ", ".join(r.pnl.boutons_chauds) if r.pnl.boutons_chauds else "aucun"
            lignes.append(f"- **Déclencheurs émotionnels** : {boutons}")
        if r.resume_ia:
            lignes.append(f"\n**Résumé** : {r.resume_ia}\n")
        if r.mot_cle:
            lignes.append(f"**Mots-clés** : {', '.join(r.mot_cle)}\n")
        personnes = ", ".join(r.entites.get("personnes", [])) or "n/a"
        organisations = ", ".join(r.entites.get("organisations", [])) or "n/a"
        lieux = ", ".join(r.entites.get("lieux", [])) or "n/a"
        lignes.append(f"**Personnes** : {personnes}")
        lignes.append(f"**Organisations** : {organisations}")
        lignes.append(f"**Lieux** : {lieux}")
        if r.note_analyste:
            lignes.append(f"\n**Note d'analyse** : {r.note_analyste}\n")
        lignes.append("\n---\n")
    chemin.write_text("\n".join(lignes), encoding="utf-8")


def _rapport_csv(resultats: list["AnalyseArticle"], chemin: Path) -> None:
    entetes = [
        "titre", "url", "source", "date_publication", "thematique", "sentiment",
        "score_sentiment", "pertinence", "resume_ia", "mot_cle",
        "score_manipulation", "niveau_manipulation", "note_analyste",
    ]
    with chemin.open("w", newline="", encoding="utf-8") as flux:
        ecrivain = csv.writer(flux, delimiter=";")
        ecrivain.writerow(entetes)
        for r in _tri(resultats):
            ecrivain.writerow([
                r.article.titre,
                r.article.url,
                r.article.source,
                r.article.date_publication,
                r.thematique,
                r.sentiment,
                r.score_sentiment,
                r.pertinence,
                r.resume_ia,
                "|".join(r.mot_cle),
                f"{r.pnl.score_manipulation:.2f}" if r.pnl else "",
                r.pnl.niveau_manipulation if r.pnl else "",
                r.note_analyste,
            ])


def _rapport_html(resultats: list["AnalyseArticle"], chemin: Path) -> None:
    cartes = []
    for r in _tri(resultats):
        categories = ", ".join(escape(c) for c in r.categories) if r.categories else "n/a"
        resume = escape(r.resume_ia) if r.resume_ia else ""
        pnl_html = ""
        if r.pnl is not None:
            boutons = ", ".join(escape(b) for b in r.pnl.boutons_chauds) or "aucun"
            pnl_html = (
                f"<p class='cats'>Analyse PNL : "
                f"{r.pnl.score_manipulation:.2f} ({escape(r.pnl.niveau_manipulation)}) "
                f"&nbsp; Déclencheurs : {boutons}</p>"
            )
        note_html = f"<p class='note'>{escape(r.note_analyste)}</p>" if r.note_analyste else ""
        cartes.append(
            f"<article><h2>{escape(r.article.titre)}</h2>"
            f"<p class='meta'>Source : <b>{escape(r.article.source)}</b> — "
            f"Thématique : <b>{escape(r.thematique)}</b> — "
            f"Pertinence : <b>{r.pertinence:.2f}</b></p>"
            f"<p>{resume}</p>"
            f"<p class='cats'>Catégories : {categories}&nbsp; Sentiment : "
            f"{escape(r.sentiment)} ({r.score_sentiment:+.2f})</p>"
            f"{pnl_html}{note_html}"
            f"</article>"
        )
    html = (
        "<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>"
        "<title>Rapport d'analyse de l'actualité</title>"
        "<style>body{font-family:system-ui;max-width:800px;margin:2rem auto;padding:0 1rem}"
        "article{border:1px solid #ddd;border-radius:8px;padding:1rem;margin:1rem 0}"
        ".cats{color:#555;font-size:.9rem}</style></head><body>"
        "<h1>Rapport d'analyse de l'actualité</h1>"
        + "".join(cartes)
        + "</body></html>"
    )
    chemin.write_text(html, encoding="utf-8")
