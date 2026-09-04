"""Agents IA du projet news-intell.

Chaque agent remplit une mission précise (résumé, classification, sentiment,
entités, pertinence) en interrogeant un modèle LocalAI. Le coordinateur
orchestre l'ensemble.
"""
from .coordinator import CoordinateurAgents

__all__ = ["CoordinateurAgents"]
