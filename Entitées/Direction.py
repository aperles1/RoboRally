"""
Auteur : Perles Alexis, Maelys Rameau
Date de dernière modification : 22/10/2026
Contenu : Définit les quatre directions de déplacement du jeu.
"""

from enum import Enum

class Direction(Enum):
    NORD = (0, -1)
    EST = (1, 0)
    SUD = (0, 1)
    OUEST = (-1, 0)


class ActionCarte(Enum):
    AVANCER = "Avancer"
    TOURNER_DROITE = "Tourner à droite"
    TOURNER_GAUCHE = "Tourner à gauche"