from Direction import Direction
from Drapeau import Drapeau
from TypeCase import TypeCase


class Case:
    def __init__(
        self,
        type_case=TypeCase.VIDE,
        murs=(),
        drapeau=None,
        rotation=None,
    ):
        self.type_case = type_case
        self.murs = list(dict.fromkeys(murs))
        self.drapeau = drapeau
        self.rotation = rotation

    def ajouter_mur(self, direction):
        if direction not in self.murs:
            self.murs.append(direction)

    def a_un_mur(self, direction):
        return direction in self.murs

    def direction_tapis(self):
        directions = {
            TypeCase.TAPIS_NORD: Direction.NORD,
            TypeCase.TAPIS_EST: Direction.EST,
            TypeCase.TAPIS_SUD: Direction.SUD,
            TypeCase.TAPIS_OUEST: Direction.OUEST,
        }
        return directions.get(self.type_case)

    def est_trou(self):
        return self.type_case == TypeCase.TROU

    def est_tapis(self):
        return self.type_case.est_tapis
