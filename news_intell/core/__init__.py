"""Cœur du projet : analystes et travailleurs (workers) pour les news."""

from .analyst import Analyste
from .workers import ParcTravailleurs, Travailleur

__all__ = ["Analyste", "ParcTravailleurs", "Travailleur"]
