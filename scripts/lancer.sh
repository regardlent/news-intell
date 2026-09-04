#!/usr/bin/env bash
# Lance l'analyse de news par agents IA (LocalAI).
# Se place automatiquement à la racine du projet.
cd "$(dirname "$0")/.." || exit 1
python -m src.cli executer --format md
