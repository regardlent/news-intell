@echo off
REM Lance l'analyse de news par agents IA (LocalAI).
REM Se place automatiquement a la racine du projet.
cd /d "%~dp0.."
python -m news_intell.cli executer --format md
