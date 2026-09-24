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
        return self in {
            TypeCase.TAPIS_NORD,
            TypeCase.TAPIS_EST,
            TypeCase.TAPIS_SUD,
            TypeCase.TAPIS_OUEST,
        }