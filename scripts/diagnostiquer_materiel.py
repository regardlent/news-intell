"""Diagnostique le matériel et recommande un modèle local « personnalisé » optimisé.

Usage :
    python scripts/diagnostiquer_materiel.py             # rapport + recommandation
    python scripts/diagnostiquer_materiel.py --ecrire    # écrit config/config.local.yaml
"""
from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
from pathlib import Path

PROJET = Path(__file__).resolve().parent.parent


class _StatutMemoire(ctypes.Structure):
    """Structure de GlobalMemoryStatusEx (Windows)."""

    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def detecter_vram() -> int:
    """VRAM totale (MiB) du GPU NVIDIA, sinon 0 (CPU seul)."""
    try:
        sortie = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10,
        )
        return int(sortie.stdout.strip().split()[0])  # déjà en MiB
    except Exception:  # noqa: BLE001
        return 0


def detecter_ram() -> float:
    """RAM totale (Go) via GlobalMemoryStatusEx (sans dépendance)."""
    try:
        statut = _StatutMemoire()
        statut.dwLength = ctypes.sizeof(_StatutMemoire)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(statut))
        return statut.ullTotalPhys / (1024**3)
    except Exception:  # noqa: BLE001
        return 0.0


def recommander(vram: int) -> str:
    """Recommande une taille/quantisation de modèle selon la VRAM."""
    if vram >= 16000:
        return "7B-8B · Q4_K_M (GPU)"
    if vram >= 8000:
        return "3B-4B · Q4_K_M (GPU)  — idéal pour 8 Go"
    if vram >= 4000:
        return "1.5B-2B · Q4_K_M (GPU)"
    return "0.5B-1.5B · Q4_K_M (CPU)"


def principale(ecrire: bool) -> int:
    cpu = os.cpu_count() or 4
    vram = detecter_vram()
    ram_go = detecter_ram()
    rec = recommander(vram)
    gpu = 999 if vram else 0

    print("=== Matériel détecté ===")
    print(f"  CPU   : {cpu} threads")
    print(f"  RAM   : {ram_go:.1f} Go")
    print(f"  VRAM  : {vram} MiB (NVIDIA)")
    print()
    print("=== Recommandation modèle local ===")
    print(f"  {rec}")
    print(f"  Réglages : nb_threads={cpu}, contexte=8192, gpu_couches={gpu}")

    if ecrire:
        (PROJET / "config").mkdir(exist_ok=True)
        contenu = (
            "# Profil matériel (généré par scripts/diagnostiquer_materiel.py)\n"
            "backend: \"personnalise\"\n"
            "modele_personnalise:\n"
            '  nom: "news-intell-expert"\n'
            '  chemin: "CHEMIN_A_REMPLACER_PAR_VOTRE_MODELE.gguf"\n'
            "llm:\n"
            f"  nb_threads: {cpu}\n"
            "  contexte: 8192\n"
            f"  gpu_couches: {gpu}\n"
        )
        (PROJET / "config" / "config.local.yaml").write_text(contenu, encoding="utf-8")
        print("\n→ config/config.local.yaml écrit (remplacez le chemin du modèle).")
    return 0


if __name__ == "__main__":
    parseur = argparse.ArgumentParser(description="Diagnostic matériel pour le modèle local.")
    parseur.add_argument("--ecrire", action="store_true", help="Écrit config/config.local.yaml")
    args = parseur.parse_args()
    raise SystemExit(principale(args.ecrire))
