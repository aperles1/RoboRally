"""
Auteur : Perles Alexis
Date de dernière modification : 30/09/2026
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

    @property
    def est_tapis(self) -> bool:
        """Indique si le type correspond à un tapis roulant.

        - Description : teste l'appartenance aux quatre types de tapis.
        - Prérequis : aucun.
        - Arguments : aucun.
        - Retourne : résultat du test (`bool`).
        """
        return self in {
            TypeCase.TAPIS_NORD,
            TypeCase.TAPIS_EST,
            TypeCase.TAPIS_SUD,
            TypeCase.TAPIS_OUEST,
        }