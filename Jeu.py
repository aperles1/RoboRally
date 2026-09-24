"""Règles centrales de RoboRally.

Ce module ne connaît pas pygame : il peut donc être testé sans dépendre de
l'interface graphique.
"""

import random

from Carte import Carte
from Case import Case
from Direction import Direction
from Drapeau import Drapeau
from Robot import Robot
from TypeCase import TypeCase


class Jeu:
    CARTES_PAR_ROBOT = 3

    def __init__(
        self,
        robots,
        largeur,
        hauteur,
        cases,
        graine=None,
    ):
        self.robots = list(robots)
        self.largeur = largeur
        self.hauteur = hauteur
        self.cases = [list(ligne) for ligne in cases]
        self.aleatoire = random.Random(graine)
        self.mains = {}
        self.cartes_du_tour = []
        self.derniers_deplacements = []
        self.drapeaux = []
        self.numero_tour = 0
        self.equipe_gagnante = None
        self.nouvelle_pioche()

    def nouvelle_pioche(self, cartes_par_robot=None):
        """Installe trois cartes choisies et les trie par priorité."""
        self.numero_tour += 1
        self.mains = cartes_par_robot or {
            id(robot): [
                Carte.aleatoire(self.aleatoire)
                for _ in range(self.CARTES_PAR_ROBOT)
            ]
            for robot in self.robots if not robot.est_detruit
        }
        self.cartes_du_tour = sorted(
            (
                (robot, carte)
                for robot in self.robots
                if not robot.est_detruit
                for carte in self.mains[id(robot)]
            ),
            key=lambda element: element[1].vitesse,
            reverse=True,
        )

    def carte_actuelle(self):
        return self.cartes_du_tour[0] if self.cartes_du_tour else None

    def deplacement_mene_au_trou(self, robot: Robot, direction: Direction) -> bool:
        """Indique si la case cible ou un tapis suivant mène à un trou."""
        if not self._passage_possible(robot.x, robot.y, direction):
            return False
        if not self._dans_plateau(
            robot.x + direction.value[0], robot.y + direction.value[1]
        ):
            return False

        x = robot.x + direction.value[0]
        y = robot.y + direction.value[1]
        visites = set()
        while (x, y) not in visites:
            visites.add((x, y))
            case = self.cases[y][x]
            if case.type_case == TypeCase.TROU:
                return True
            if not case.type_case.est_tapis:
                return False
            tapis_direction = case.direction_tapis()
            x += tapis_direction.value[0]
            y += tapis_direction.value[1]
            if not self._dans_plateau(x, y):
                return False
        return False

    def tableau_plateau(self):
        """Encode chaque case en vecteur numérique de longueur 16.

        Les positions sont fixes afin que le perceptron lise toujours les
        mêmes colonnes : vide, trou, bonus, réparation, quatre tapis, robot
        bleu, robot rouge, drapeau neutre, drapeau capturé et quatre murs.
        """
        tableau = []
        for y, ligne in enumerate(self.cases):
            ligne_encodee = []
            for x, case in enumerate(ligne):
                vecteur = [0.0] * 16
                index_type = {
                    TypeCase.VIDE: 0,
                    TypeCase.TROU: 1,
                    TypeCase.BONUS: 2,
                    TypeCase.REPARATION: 3,
                    TypeCase.TAPIS_NORD: 4,
                    TypeCase.TAPIS_EST: 5,
                    TypeCase.TAPIS_SUD: 6,
                    TypeCase.TAPIS_OUEST: 7,
                }[case.type_case]
                vecteur[index_type] = 1.0
                robots = [robot for robot in self.robots if not robot.est_detruit]
                robot_sur_case = next(
                    (robot for robot in robots if (robot.x, robot.y) == (x, y)),
                    None,
                )
                if robot_sur_case is not None:
                    vecteur[8 if robot_sur_case.couleur == "bleu" else 9] = 1.0
                for drapeau, drapeau_x, drapeau_y in self.drapeaux:
                    if (x, y) == (drapeau_x, drapeau_y):
                        vecteur[10 if drapeau.couleur == "neutre" else 11] = 1.0
                for index_mur, direction in enumerate(Direction):
                    if case.a_un_mur(direction):
                        vecteur[12 + index_mur] = 1.0
                ligne_encodee.append(vecteur)
            tableau.append(ligne_encodee)
        return tableau

    def jouer_carte_actuelle(self, jouer):
        """Joue ou retire la carte visible, puis révèle la suivante."""
        actuelle = self.carte_actuelle()
        if actuelle is None:
            return None
        robot, carte = actuelle
        self.cartes_du_tour.pop(0)
        self.mains[id(robot)].remove(carte)
        self.derniers_deplacements = []
        if jouer and not robot.est_detruit:
            robot.direction = carte.direction
            self._avancer(robot, carte.direction, set())
            self._tirer(robot)
        self._actualiser_victoire()
        if not self.cartes_du_tour:
            self._actualiser_victoire()
        return robot

    def _actualiser_victoire(self) -> None:
        """Détermine la victoire par drapeaux ou par élimination."""
        equipes = {robot.couleur for robot in self.robots}
        for equipe in equipes:
            if self.drapeaux and all(drapeau.couleur == equipe for drapeau, _, _ in self.drapeaux):
                self.equipe_gagnante = equipe
                return
            if all(robot.est_detruit or robot.couleur == equipe for robot in self.robots):
                self.equipe_gagnante = equipe
                return

    def _avancer(
        self, robot, direction, tapis_visites
    ):
        if robot.est_detruit or not self._passage_possible(robot.x, robot.y, direction):
            return False
        cible = self._robot_a(robot.x + direction.value[0], robot.y + direction.value[1])
        if cible is not None and not self._pousser(cible, direction, set()):
            return False
        if self._robot_a(robot.x + direction.value[0], robot.y + direction.value[1]) is not None:
            return False
        self._deplacer(robot, direction)
        self._effet_case(robot, tapis_visites)
        return True

    def _pousser(self, robot, direction, visites):
        if id(robot) in visites or not self._passage_possible(robot.x, robot.y, direction):
            return False
        visites.add(id(robot))
        cible = self._robot_a(robot.x + direction.value[0], robot.y + direction.value[1])
        if cible is not None and not self._pousser(cible, direction, visites):
            return False
        if self._robot_a(robot.x + direction.value[0], robot.y + direction.value[1]) is not None:
            return False
        self._deplacer(robot, direction)
        self._effet_case(robot, set())
        return True

    def _deplacer(self, robot: Robot, direction: Direction) -> None:
        ancienne = (robot.x, robot.y)
        nouvelle = (
            robot.x + direction.value[0],
            robot.y + direction.value[1],
        )
        occupant = self._robot_a(*nouvelle)
        if occupant is not None and occupant is not robot:
            return False
        robot.deplacer(direction)
        self.derniers_deplacements.append((robot, ancienne, (robot.x, robot.y)))
        return True

    def _effet_case(self, robot, tapis_visites):
        """Applique le terrain, puis avance d'une case par tapis roulant."""
        case = self.cases[robot.y][robot.x]
        if case.type_case == TypeCase.TROU:
            robot.est_detruit = True
            return
        if case.type_case == TypeCase.REPARATION:
            robot.utiliser_case_bonus("reparation", self.aleatoire)
            case.type_case = TypeCase.VIDE
        elif case.type_case == TypeCase.BONUS:
            robot.utiliser_case_bonus("bonus", self.aleatoire)
            case.type_case = TypeCase.VIDE
        self._capturer_drapeau(robot)
        if case.type_case.est_tapis and (robot.x, robot.y) not in tapis_visites:
            tapis_visites.add((robot.x, robot.y))
            self._avancer(robot, case.direction_tapis(), tapis_visites)

    def _capturer_drapeau(self, robot: Robot) -> None:
        for drapeau, x, y in self.drapeaux:
            if (robot.x, robot.y) == (x, y):
                drapeau.couleur = robot.couleur

    def _tirer(self, robot):
        """Tire seulement sur un adversaire aligné : les équipiers sont ignorés."""
        x, y = robot.x, robot.y
        while self._dans_plateau(x + robot.direction.value[0], y + robot.direction.value[1]):
            if not self._passage_possible(x, y, robot.direction):
                return None
            x += robot.direction.value[0]
            y += robot.direction.value[1]
            cible = self._robot_a(x, y)
            if cible is not None:
                if cible.couleur != robot.couleur:
                    cible.recoit_degats(1 + robot.bonus_degats)
                    robot.bonus_degats = 0
                    return cible
                return None
        return None

    def _passage_possible(self, x: int, y: int, direction: Direction) -> bool:
        nx, ny = x + direction.value[0], y + direction.value[1]
        if not self._dans_plateau(nx, ny):
            return False
        opposee = {
            Direction.NORD: Direction.SUD, Direction.EST: Direction.OUEST,
            Direction.SUD: Direction.NORD, Direction.OUEST: Direction.EST,
        }[direction]
        return not (
            self.cases[y][x].a_un_mur(direction)
            or self.cases[ny][nx].a_un_mur(opposee)
        )

    def _dans_plateau(self, x: int, y: int) -> bool:
        return 0 <= x < self.largeur and 0 <= y < self.hauteur

    def _robot_a(self, x, y):
        return next((r for r in self.robots if not r.est_detruit and (r.x, r.y) == (x, y)), None)
