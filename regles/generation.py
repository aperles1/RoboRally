"""
Auteur : Perles Alexis
Date de dernière modification : 10/11/2026
Contenu : Construit le plateau fixe du jeu.
"""

from entites.case import Case
from entites.direction import Direction
from entites.type_case import TypeCase, est_tapis


TAILLE_PLATEAU = 12


def creer_plateau(graine=None):
    """
    Role : construit la carte fixe et ses obstacles.
    Entrees : graine (int ou None) : graine reservee pour compatibilite
    Sorties : tuple : cases et murs du plateau
    Pré-requis : aucun
    """
    cases = [[Case() for _ in range(TAILLE_PLATEAU)] for _ in range(TAILLE_PLATEAU)]
    tapis = {
        (3, 2): (TypeCase.TAPIS_EST, None), (4, 2): (TypeCase.TAPIS_EST, None),
        (5, 2): (TypeCase.TAPIS_NORD, 180), (5, 1): (TypeCase.TAPIS_NORD, None),
        (5, 0): (TypeCase.TAPIS_NORD, None), (6, 9): (TypeCase.TAPIS_OUEST, None),
        (5, 9): (TypeCase.TAPIS_OUEST, None), (4, 9): (TypeCase.TAPIS_SUD, 0),
        (4, 10): (TypeCase.TAPIS_SUD, None), (4, 11): (TypeCase.TAPIS_SUD, None),
        (2, 4): (TypeCase.TAPIS_SUD, None), (2, 5): (TypeCase.TAPIS_SUD, None),
        (2, 6): (TypeCase.TAPIS_EST, 90), (3, 6): (TypeCase.TAPIS_EST, None),
        (4, 6): (TypeCase.TAPIS_EST, None), (9, 4): (TypeCase.TAPIS_NORD, None),
        (9, 5): (TypeCase.TAPIS_NORD, None), (9, 6): (TypeCase.TAPIS_NORD, 180),
        (8, 6): (TypeCase.TAPIS_EST, None), (7, 6): (TypeCase.TAPIS_EST, None),
    }
    for (x, y), (type_case, rotation) in tapis.items():
        cases[y][x] = Case(type_case, rotation=rotation)
    trous = {(1, 4), (5, 5), (8, 3), (3, 9), (10, 6)}
    for x, y in trous:
        if (x, y) not in tapis:
            cases[y][x] = Case(TypeCase.TROU)
    _placer_cases(cases, tapis, trous, {(0, 0), (1, 0), (10, 11), (11, 11)},
                  {(2, 1), (5, 4), (9, 8)}, TypeCase.BONUS)
    _placer_cases(cases, tapis, trous, {(0, 0), (1, 0), (10, 11), (11, 11)},
                  {(4, 7), (7, 4), (10, 8)}, TypeCase.REPARATION)
    murs = _placer_murs(cases)
    return cases, murs


def _placer_cases(cases, tapis, trous, depart, positions, type_case):
    """
    Role : place un type de case sur les positions disponibles.
    Entrees : cases (list) : plateau ; tapis (set) : tapis ; trous (set) : trous ; depart (set) : departs ; positions (set) : positions ; type_case (TypeCase) : type a placer
    Sorties : aucune
    Pré-requis : les positions sont dans le plateau
    """
    for x, y in positions:
        if (x, y) not in tapis and (x, y) not in trous and (x, y) not in depart:
            cases[y][x] = Case(type_case)


def _placer_murs(cases):
    """
    Role : place les murs fixes sur les cases vides.
    Entrees : cases (list) : plateau a modifier
    Sorties : dict : murs indexes par position
    Pré-requis : cases est un plateau de 12 par 12
    """
    emplacements = [
        ((0, 2), Direction.NORD), ((3, 3), Direction.EST),
        ((6, 3), Direction.SUD), ((9, 3), Direction.OUEST),
        ((4, 5), Direction.NORD), ((6, 6), Direction.EST),
        ((8, 6), Direction.SUD), ((3, 7), Direction.OUEST),
        ((6, 9), Direction.NORD), ((11, 8), Direction.EST),
        ((4, 11), Direction.SUD), ((10, 10), Direction.OUEST),
    ]
    murs = {}
    for (x, y), direction in emplacements:
        if cases[y][x].type_case == TypeCase.VIDE:
            murs[(x, y)] = {direction}
            cases[y][x].ajouter_mur(direction)
    return murs
