from collections.abc import Iterable

from Direction import Direction
from Drapeau import Drapeau
from TypeCase import TypeCase


class Case:
    def __init__(
        self,
        type_case: TypeCase = TypeCase.VIDE,
        murs: Iterable[Direction] = (),
        drapeau: Drapeau | None = None,
    ):
        self.type_case = type_case
        self.murs = list(dict.fromkeys(murs))
        self.drapeau = drapeau

    def ajouter_mur(self, direction: Direction) -> None:
        if direction not in self.murs:
            self.murs.append(direction)

    def a_un_mur(self, direction: Direction) -> bool:
        return direction in self.murs
