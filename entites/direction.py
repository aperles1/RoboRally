"""
Auteur : Perles Alexis, Maelys Rameau
Date de dernière modification : 10/11/2026
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


def tourner_droite(direction):
    """
    Role : tourne une direction d'un quart de tour vers la droite.
    Entrees : direction (Direction) : direction initiale
    Sorties : Direction : direction obtenue
    Pré-requis : direction est une direction cardinale
    """
    ordre = (Direction.NORD, Direction.EST, Direction.SUD, Direction.OUEST)
    return ordre[(ordre.index(direction) + 1) % 4]


def tourner_gauche(direction):
    """
    Role : tourne une direction d'un quart de tour vers la gauche.
    Entrees : direction (Direction) : direction initiale
    Sorties : Direction : direction obtenue
    Pré-requis : direction est une direction cardinale
    """
    ordre = (Direction.NORD, Direction.OUEST, Direction.SUD, Direction.EST)
    return ordre[(ordre.index(direction) + 1) % 4]