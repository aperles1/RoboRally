"""
Auteur : Perles Alexis
Date de dernière modification : 30/09/2026
Contenu : Modélise les cases du plateau, leurs terrains et leurs murs.
"""

from Direction import Direction
from TypeCase import TypeCase


class Case:
    """Représente une case du plateau et ses éventuels éléments."""

    def __init__(
        self,
        type_case=TypeCase.VIDE,
        murs=(),
        drapeau=None,
        rotation=None,
    ):
        """Construit une case avec son terrain et ses murs.

        - Description : initialise les propriétés d'une case du plateau.
        - Prérequis : `type_case` doit être un membre de `TypeCase` et
          `murs` doit contenir des directions valides.
        - Arguments : `type_case` (`TypeCase`), `murs` (itérable de
          `Direction`), `drapeau` (`Drapeau` ou `None`) et `rotation`
          (`int` ou `None`).
        - Retourne : rien (`None`).
        """
        self.type_case = type_case
        self.murs = list(dict.fromkeys(murs))
        self.drapeau = drapeau
        self.rotation = rotation

    def ajouter_mur(self, direction):
        """Ajoute un mur à la case s'il n'est pas déjà présent.

        - Description : complète la liste des murs de la case sans doublon.
        - Prérequis : `direction` doit être une valeur de `Direction`.
        - Arguments : `direction` (`Direction`).
        - Retourne : rien (`None`).
        """
        if direction not in self.murs:
            self.murs.append(direction)

    def a_un_mur(self, direction):
        """Vérifie la présence d'un mur dans une direction.

        - Description : recherche un mur parmi ceux associés à la case.
        - Prérequis : `direction` doit être une valeur de `Direction`.
        - Arguments : `direction` (`Direction`).
        - Retourne : présence du mur (`bool`).
        """
        return direction in self.murs

    def direction_tapis(self):
        """Retourne la direction de déplacement du tapis de la case.

        - Description : associe le type de tapis à sa direction.
        - Prérequis : l'objet doit être initialisé avec un `TypeCase` valide.
        - Arguments : aucun.
        - Retourne : direction du tapis (`Direction`) ou `None`.
        """
        directions = {
            TypeCase.TAPIS_NORD: Direction.NORD,
            TypeCase.TAPIS_EST: Direction.EST,
            TypeCase.TAPIS_SUD: Direction.SUD,
            TypeCase.TAPIS_OUEST: Direction.OUEST,
        }
        return directions.get(self.type_case)

    def est_trou(self):
        """Indique si la case est un trou.

        - Description : compare le type de la case avec `TypeCase.TROU`.
        - Prérequis : aucun.
        - Arguments : aucun.
        - Retourne : résultat du test (`bool`).
        """
        return self.type_case == TypeCase.TROU

    def est_tapis(self):
        """Indique si la case est un tapis roulant.

        - Description : utilise la propriété `est_tapis` du type de case.
        - Prérequis : aucun.
        - Arguments : aucun.
        - Retourne : résultat du test (`bool`).
        """
        return self.type_case.est_tapis
