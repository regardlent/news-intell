"""Télécharge et configure un modèle local GGUF optimisé pour le matériel.

Usage :
    python scripts/installer_modele_local.py               # recommande + télécharge + configure
    python scripts/installer_modele_local.py --modele 3b   # force 1.5b / 3b / 7b
    python scripts/installer_modele_local.py --seuil 0.8   # seuil de vérification (Go)
"""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

import requests

PROJET = Path(__file__).resolve().parent.parent
DOSSIER_MODELE = PROJET / "modele"
CONFIG_LOCAL = PROJET / "config" / "config.local.yaml"

# (repo HuggingFace, fichier GGUF, taille approximative en Go)
MODELES = {
    "0.5b": ("Qwen/Qwen2.5-0.5B-Instruct-GGUF", "qwen2.5-0.5b-instruct-q4_k_m.gguf", 0.4),
    "1.5b": ("Qwen/Qwen2.5-1.5B-Instruct-GGUF", "qwen2.5-1.5b-instruct-q4_k_m.gguf", 1.0),
    "3b": ("Qwen/Qwen2.5-3B-Instruct-GGUF", "qwen2.5-3b-instruct-q4_k_m.gguf", 1.9),
    "7b": ("Qwen/Qwen2.5-7B-Instruct-GGUF", "qwen2.5-7b-instruct-q4_k_m.gguf", 4.7),
}


def detecter_vram() -> int:
    """VRAM (MiB) du GPU NVIDIA, sinon 0 (CPU seul)."""
    try:
        sortie = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        return int(sortie.stdout.strip().split()[0])
    except Exception:  # noqa: BLE001
        return 0


def choisir_modele(vram: int) -> str:
    """Choisit une taille de modèle selon la VRAM."""
    if vram >= 12000:
        return "7b"
    if vram >= 8000:
        return "3b"
    if vram >= 4000:
        return "1.5b"
    return "0.5b"


def telecharger(url: str, destination: Path) -> Path:
    """Télécharge un fichier avec affichage de progression."""
    DOSSIER_MODELE.mkdir(exist_ok=True)
    print(f"Téléchargement de {url} …")
    try:
        reponse = requests.get(url, stream=True, timeout=60)
        reponse.raise_for_status()
        total = int(reponse.headers.get("content-length", 0))
        telecharge = 0
        with destination.open("wb") as flux:
            for bloc in reponse.iter_content(chunk_size=1024 * 256):
                if not bloc:
                    continue
                flux.write(bloc)
                telecharge += len(bloc)
                if total:
                    pourcent = telecharge * 100 // max(total, 1)
                    print(f"\r  {pourcent:>3} %  ({telecharge / 1e6:.0f} Mo)", end="")
        print()
        return destination
    except requests.RequestException as exc:
        raise RuntimeError(f"Échec du téléchargement : {exc}") from exc


def ecrire_config_local(chemin_modele: str, cle: str, vram: int, n_threads: int) -> None:
    """Écrit un profil matériel activant le backend « personnalise »."""
    (PROJET / "config").mkdir(exist_ok=True)
    contenu = (
        "# Profil matériel (généré par scripts/installer_modele_local.py)\n"
        'backend: "personnalise"\n'
        "modele_personnalise:\n"
        f'  nom: "news-intell-{cle}"\n'
        f'  chemin: "{chemin_modele}"\n'
        "llm:\n"
        f"  nb_threads: {n_threads}\n"
        "  contexte: 8192\n"
        f"  gpu_couches: {'999' if vram else '0'}\n"
    )
    CONFIG_LOCAL.write_text(contenu, encoding="utf-8")
    print(f"→ config/config.local.yaml écrit ({CONFIG_LOCAL}).")


def verifier_et_tester(chemin: Path, seuil_go: float) -> None:
    """Vérifie la taille puis tente une génération si llama-cpp-python est installé."""
    taille = chemin.stat().st_size / (1024**3)
    print(f"Taille téléchargée : {taille:.2f} Go")
    if taille < seuil_go:
        print("⚠ Taille inférieure au seuil attendu — fichier incomplet ou erreur.")

    try:
        from llama_cpp import Llama  # noqa: WPS433
    except ImportError:
        print("ℹ llama-cpp-python non installé : installez-le puis relancez ce script.")
        return
    llm = Llama(model_path=str(chemin), n_ctx=2048, n_threads=os.cpu_count() or 4)
    sortie = llm("[INST] Réponds en un seul mot français. [/INST]", max_tokens=16, temperature=0.0)
    print("Test de génération :", sortie["choices"][0]["text"].strip()[:60])


def principale(cle: str, seuil_go: float) -> int:
    vram = detecter_vram()
    n_threads = os.cpu_count() or 4
    if cle == "auto":
        cle = choisir_modele(vram)

    if cle not in MODELES:
        print(f"✖ Modèle inconnu : {cle} (choix : {', '.join(MODELES)} ou auto).")
        return 1

    repo, fichier, taille = MODELES[cle]
    url = f"https://huggingface.co/{repo}/resolve/main/{fichier}"
    destination = DOSSIER_MODELE / fichier

    print(f"=== Modèle recommandé : {cle} ({taille:.1f} Go) · VRAM {vram} MiB ===")
    telecharger(url, destination)
    ecrire_config_local(str(destination), cle, vram, n_threads)
    verifier_et_tester(destination, seuil_go)
    print("✔ Terminé. Relancez `python -m news_intell.cli serveur` puis vérifiez.")
    return 0


if __name__ == "__main__":
    parseur = argparse.ArgumentParser(description="Installe un modèle local GGUF optimisé.")
    parseur.add_argument(
        "--modele", default="auto",
        help="Taille du modèle (0.5b / 1.5b / 3b / 7b ou auto).",
    )
    parseur.add_argument("--seuil", type=float, default=0.5, help="Seuil de taille (Go).")
    args = parseur.parse_args()
    raise SystemExit(principale(args.modele, args.seuil))
