"""Récupération d'articles depuis des flux RSS / Atom.

Le module s'appuie sur la bibliothèque `requests` (déjà utilisée ailleurs
dans le projet) et sur la bibliothèque standard `xml.etree.ElementTree`.
"""
from __future__ import annotations

import urllib.parse
import xml.etree.ElementTree as ET
from typing import Any

import requests

from ..models import Article


def _url_absolue(base: str, valeur: str) -> str:
    """Convertit un chemin relatif ou une URL absolue."""
    if not valeur:
        return valeur
    if "://" in valeur:
        return valeur
    return urllib.parse.urljoin(base, valeur)


def _texte(noeud: ET.Element, balise: str, defaut: str = "") -> str:
    """Récupère le texte d'un sous-élément, avec valeur par défaut."""
    enfant = noeud.find(balise)
    if enfant is None or enfant.text is None:
        return defaut
    return enfant.text.strip()


def analyser_flux_xml(contenu: str, base_url: str, nom_source: str) -> list[Article]:
    """Analyse le XML d'un flux RSS ou Atom et renvoie une liste d'articles."""
    articles: list[Article] = []
    try:
        racine = ET.fromstring(contenu)
    except ET.ParseError:
        return articles

    items = racine.findall(".//item")
    entrees = racine.findall(".//{http://www.w3.org/2005/Atom}entry")

    if items:
        for item in items:
            titre = _texte(item, "title")
            lien = _texte(item, "link")
            description = _texte(item, "description")
            date_pub = _texte(item, "pubDate")
            articles.append(
                Article(
                    titre=titre,
                    url=_url_absolue(base_url, lien),
                    source=nom_source,
                    resume=description,
                    contenu=description,
                    date_publication=date_pub,
                )
            )
    elif entrees:
        ns = "{http://www.w3.org/2005/Atom}"
        for entree in entrees:
            titre = (entree.findtext(f"{ns}title") or "").strip()
            lien_elem = entree.find(f"{ns}link")
            href = lien_elem.get("href") if lien_elem is not None else ""
            resume = (entree.findtext(f"{ns}summary") or "").strip()
            date_pub = (entree.findtext(f"{ns}updated") or "").strip()
            articles.append(
                Article(
                    titre=titre,
                    url=_url_absolue(base_url, href),
                    source=nom_source,
                    resume=resume,
                    contenu=resume,
                    date_publication=date_pub,
                )
            )
    return articles


def recuperer_flux(url: str, nom_source: str, timeout: int = 20) -> list[Article]:
    """Télécharge un flux RSS/Atom et renvoie ses articles."""
    try:
        reponse = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "news-intell/1.0"},
        )
        reponse.raise_for_status()
        reponse.encoding = reponse.apparent_encoding or "utf-8"
        return analyser_flux_xml(reponse.text, url, nom_source)
    except requests.RequestException:
        return []


def charger_depuis_config(source: dict[str, Any], timeout: int = 20) -> list[Article]:
    """Récupère les articles d'une source décrite par un dictionnaire de config."""
    url = source.get("url", "")
    nom_source = source.get("nom", url)
    return recuperer_flux(url, nom_source, timeout=timeout)
