"""
Auteur : Perles Alexis
Date de dernière modification : 10/11/2026
Contenu : Modélise les cases, leurs terrains et leurs murs.
"""

from dataclasses import dataclass, field

from entites.direction import Direction
from entites.type_case import TypeCase, est_tapis


@dataclass
class Case:
    type_case: TypeCase = TypeCase.VIDE
    murs: list = field(default_factory=list)
    drapeau: str = None
    rotation: int = None

    def __post_init__(self):
        """
        Role : supprime les murs en double lors de la creation.
        Entrees : aucune
        Sorties : aucune
        Pré-requis : murs contient des directions
        """
        self.murs = list(dict.fromkeys(self.murs))

    def ajouter_mur(self, direction):
        """
        Role : ajoute un mur a la case.
        Entrees : direction (Direction) : direction du mur
        Sorties : aucune
        Pré-requis : direction est une valeur de Direction
        """
        if direction not in self.murs:
            self.murs.append(direction)

    def a_un_mur(self, direction):
        """
        Role : teste la presence d'un mur.
        Entrees : direction (Direction) : direction a tester
        Sorties : bool : presence du mur
        Pré-requis : direction est une valeur de Direction
        """
        return direction in self.murs

    def direction_tapis(self):
        """
        Role : retourne la direction du tapis de la case.
        Entrees : aucune
        Sorties : Direction ou None : direction du tapis
        Pré-requis : type_case est valide
        """
        directions = {
            TypeCase.TAPIS_NORD: Direction.NORD,
            TypeCase.TAPIS_EST: Direction.EST,
            TypeCase.TAPIS_SUD: Direction.SUD,
            TypeCase.TAPIS_OUEST: Direction.OUEST,
        }
        return directions.get(self.type_case)

    def est_trou(self):
        """
        Role : teste si la case est un trou.
        Entrees : aucune
        Sorties : bool : vrai si la case est un trou
        Pré-requis : aucun
        """
        return self.type_case == TypeCase.TROU

    def est_tapis(self):
        """
        Role : teste si la case est un tapis.
        Entrees : aucune
        Sorties : bool : vrai si la case est un tapis
        Pré-requis : aucun
        """
        return est_tapis(self.type_case)
