"""
Auteur : Perles Alexis
Date de dernière modification : 30/09/2026
Contenu : Définit les quatre directions de déplacement du jeu.
"""

from enum import Enum


class Direction(Enum):
    NORD = (0, -1)
    EST = (1, 0)
    SUD = (0, 1)
    OUEST = (-1, 0)