"""Point d'entrée du projet : permet `python -m news_intell`."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
