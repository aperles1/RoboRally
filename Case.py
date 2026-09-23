from Direction import Direction
from Drapeau import Drapeau
from TypeCase import TypeCase


class Case:
    def __init__(self, type_case: TypeCase = TypeCase.VIDE):
        self.type_case = type_case
        self.murs: list[Direction] = []
        self.drapeau: Drapeau
