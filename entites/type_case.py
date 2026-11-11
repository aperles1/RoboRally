"""
Auteur : Perles Alexis
Date de dernière modification : 10/11/2026
Contenu : Définit les types de cases disponibles sur le plateau.
"""

from enum import Enum


class TypeCase(Enum):
    VIDE = "Vide"
    TROU = "Trou"
    REPARATION = "Réparation"
    BONUS = "Bonus"
    TAPIS_NORD = "Tapis nord"
    TAPIS_EST = "Tapis est"
    TAPIS_SUD = "Tapis sud"
    TAPIS_OUEST = "Tapis ouest"


def est_tapis(type_case):
    """
    Role : indique si un type de case est un tapis roulant.
    Entrees : type_case (TypeCase) : type de terrain
    Sorties : bool : vrai pour un tapis
    Pré-requis : type_case est une valeur de TypeCase
    """
    return type_case in {
        TypeCase.TAPIS_NORD,
        TypeCase.TAPIS_EST,
        TypeCase.TAPIS_SUD,
        TypeCase.TAPIS_OUEST,
    }
