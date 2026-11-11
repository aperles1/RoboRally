"""
Auteur : Perles Alexis
Date de dernière modification : 10/11/2026
Contenu : Contient les règles, les déplacements et les combats de RoboRally.
"""

"""Règles centrales de RoboRally.

Ce module ne connaît pas pygame : il peut donc être testé sans dépendre de
l'interface graphique.
"""

import random

from entites.carte import tirer_main
from entites.direction import Direction, ActionCarte
from entites.robot import Robot
from entites.type_case import TypeCase, est_tapis
from regles.deplacements import avancer, faire_avancer_les_tapis
from regles.tir import tirer


class Jeu:
    CARTES_PAR_ROBOT = 3
    CARTES_A_TIRER = 5

    def __init__(
        self,
        robots,
        largeur,
        hauteur,
        cases,
        graine=None,
    ):
        """
        Role : copie le plateau, configure le hasard et les collections de jeu.
        Entrees : `robots` (`list[Robot]`), `largeur` (`int`), `hauteur` (`int`), `cases` (`list[list[Case]]`), `graine` (`int` ou `None`).
        Sorties : rien (`None`).
        Pré-requis : `cases` doit représenter un plateau rectangulaire.
        """
        self.robots = list(robots)
        self.largeur = largeur
        self.hauteur = hauteur
        self.cases = [list(ligne) for ligne in cases]
        self.aleatoire = random.Random(graine)
        self.mains = {}
        self.cartes_du_tour = []
        self._fins_de_manche = []
        self.drapeaux = []
        self.numero_tour = 0
        self.equipe_gagnante = None
        self.animation_callback = None
        self.tir_callback = None
        self.signature_plateau = None
        self.distance_actions_cache = {}
        self.nouvelle_pioche()

    def nouvelle_pioche(self, cartes_par_robot=None):
        """
        Role : tire cinq cartes aléatoires ou utilise les cartes fournies, puis organise les cartes en manches, une carte par robot et par manche.
        Entrees : `cartes_par_robot` (`dict[int, list[Carte]]` ou `None`).
        Sorties : rien (`None`).
        Pré-requis : les robots doivent posséder l'attribut `est_detruit`.
        """
        self.numero_tour += 1
        # Chaque robot reçoit cinq cartes possibles, puis n'en conserve que trois.
        self.mains = cartes_par_robot or {
            id(robot): self.aleatoire.sample(
                tirer_main(self.aleatoire, self.CARTES_A_TIRER),
                self.CARTES_PAR_ROBOT,
            )
            for robot in self.robots if not robot.est_detruit
        }
        self.cartes_du_tour = []
        self._fins_de_manche = []
        self._organiser_cartes_par_manches()

    def installer_cartes(self, cartes_par_robot):
        """
        Role : associe les cartes aux robots actifs et les organise en manches, une carte par robot et par manche, selon la vitesse.
        Entrees : `cartes_par_robot` (`dict[int, list[Carte]]`).
        Sorties : rien (`None`).
        Pré-requis : les clés du dictionnaire doivent être des identifiants de robots.
        """
        self.numero_tour += 1
        self.mains = {
            id(robot): list(cartes_par_robot.get(id(robot), []))
            for robot in self.robots
            if not robot.est_detruit
        }
        self.cartes_du_tour = []
        self._fins_de_manche = []
        self._organiser_cartes_par_manches()

    def _organiser_cartes_par_manches(self):
        """
        Role : aucun
        Entrees : aucune
        Sorties : aucune
        Pré-requis : aucun
        """
        mains_triees = {
            id(robot): sorted(
                self.mains[id(robot)],
                key=lambda carte: carte.vitesse,
                reverse=True,
            )
            for robot in self.robots
            if not robot.est_detruit
        }
        nombre_de_manches = max(
            (len(cartes) for cartes in mains_triees.values()),
            default=0,
        )
        for index_manche in range(nombre_de_manches):
            manche = [
                (robot, mains_triees[id(robot)][index_manche])
                for robot in self.robots
                if (
                    not robot.est_detruit
                    and index_manche < len(mains_triees[id(robot)])
                )
            ]
            manche.sort(key=lambda element: element[1].vitesse, reverse=True)
            self.cartes_du_tour.extend(manche)
            self._fins_de_manche.extend(
                index == len(manche) - 1 for index in range(len(manche))
            )

    def carte_actuelle(self):
        """
        Role : lit le premier élément de la file des cartes du tour.
        Entrees : aucun.
        Sorties : couple robot-carte (`tuple[Robot, Carte]`) ou `None`.
        Pré-requis : aucun.
        """
        return self.cartes_du_tour[0] if self.cartes_du_tour else None

    def deplacement_mene_au_trou(self, robot: Robot, direction: Direction) -> bool:
        """
        Role : suit la case cible et les tapis successifs jusqu'à un arrêt.
        Entrees : `robot` (`Robot`), `direction` (`Direction`).
        Sorties : déplacement dangereux ou non (`bool`).
        Pré-requis : `robot` doit être présent sur le plateau.
        """
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
            if not self._dans_plateau(x, y):
                return False
            visites.add((x, y))
            case = self.cases[y][x]
            if case.type_case == TypeCase.TROU:
                return True
            if not est_tapis(case.type_case):
                return False
            tapis_direction = case.direction_tapis()
            x += tapis_direction.value[0]
            y += tapis_direction.value[1]
            if not self._dans_plateau(x, y):
                return False
        return False

    def dans_plateau(self, x, y):
        """
        Role : teste si une position appartient au plateau.
        Entrees : x (int) : abscisse ; y (int) : ordonnee
        Sorties : bool : position valide
        Pré-requis : aucun
        """
        return self._dans_plateau(x, y)

    def passage_possible(self, x, y, direction):
        """
        Role : teste si un passage est libre entre deux cases.
        Entrees : x (int) : abscisse ; y (int) : ordonnee ; direction (Direction) : direction
        Sorties : bool : passage libre
        Pré-requis : x et y sont dans le plateau
        """
        return self._passage_possible(x, y, direction)

    def tableau_plateau(self):
        """
        Role : transforme chaque case, robot, drapeau et mur en 16 indicateurs (vide, trou, bonus, réparation, tapis, robots, drapeaux et murs).
        Entrees : aucun.
        Sorties : tableau encodé (`list[list[list[float]]]`).
        Pré-requis : les dimensions de `cases` doivent correspondre au plateau.
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
                # Un seul robot peut occuper une case dans l'état normal du jeu.
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
        """
        Role : retire la carte, déplace et fait tirer le robot si demandé, puis actualise la victoire.
        Entrees : `jouer` (`bool`).
        Sorties : robot concerné (`Robot`) ou `None`.
        Pré-requis : la file des cartes doit contenir des cartes valides.
        """
        actuelle = self.carte_actuelle()
        if actuelle is None:
            return None
        robot, carte = actuelle
        self.cartes_du_tour.pop(0)
        fin_de_manche = self._fins_de_manche.pop(0)
        self.mains[id(robot)].remove(carte)
        if jouer and not robot.est_detruit:
            robot.actions_recentes.append(carte.action)
            del robot.actions_recentes[:-4]
            if carte.action == ActionCarte.AVANCER:
                avancer(self, robot, robot.orientation, set())
            elif carte.action in (
                ActionCarte.TOURNER_DROITE,
                ActionCarte.TOURNER_GAUCHE,
            ):
                robot.executer_action(carte.action)
            tirer(self, robot)
        if fin_de_manche and self.equipe_gagnante is None:
            faire_avancer_les_tapis(self)
        self._actualiser_victoire()
        if not self.cartes_du_tour:
            self._actualiser_victoire()
        return robot

    def _actualiser_victoire(self) -> None:
        """
        Role : vérifie si tous les drapeaux ont la même couleur ou si les adversaires sont éliminés.
        Entrees : aucun.
        Sorties : rien (`None`).
        Pré-requis : les robots et drapeaux doivent être cohérents.
        """
        equipes = dict.fromkeys(robot.couleur for robot in self.robots)
        for equipe in equipes:
            if self.drapeaux and all(
                drapeau.couleur == equipe for drapeau, _, _ in self.drapeaux
            ):
                self.equipe_gagnante = equipe
                return
            if all(robot.est_detruit or robot.couleur == equipe for robot in self.robots):
                self.equipe_gagnante = equipe
                return

    def _avancer(
        self, robot, direction, tapis_visites
    ):
        """
        Role : vérifie le passage, pousse un robot si nécessaire, puis avance.
        Entrees : `robot` (`Robot`), `direction` (`Direction`), `tapis_visites` (`set[tuple[int, int]]`).
        Sorties : déplacement effectué (`bool`).
        Pré-requis : `robot` doit appartenir à la partie.
        """
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
        """
        Role : libère la case suivante avant de déplacer le robot courant.
        Entrees : `robot` (`Robot`), `direction` (`Direction`), `visites` (`set[int]`).
        Sorties : poussée effectuée (`bool`).
        Pré-requis : `robot` doit être actif et `direction` valide.
        """
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

    def _deplacer(self, robot: Robot, direction: Direction) -> bool:
        """
        Role : met à jour les coordonnées, l'historique et l'animation.
        Entrees : `robot` (`Robot`), `direction` (`Direction`).
        Sorties : déplacement effectué (`bool`).
        Pré-requis : la nouvelle position doit être libre.
        """
        ancienne = (robot.x, robot.y)
        nouvelle = (
            robot.x + direction.value[0],
            robot.y + direction.value[1],
        )
        occupant = self._robot_a(*nouvelle)
        if occupant is not None and occupant is not robot:
            return False
        robot.deplacer(direction)
        robot.positions_recentes.append((robot.x, robot.y))
        del robot.positions_recentes[:-6]
        if self.animation_callback is not None:
            self.animation_callback()
        self._faire_tirer_ennemis_sur(robot)
        return True

    def _effet_case(self, robot, tapis_visites):
        """
        Role : gère les trous, bonus, réparations, drapeaux, tapis et changements d'orientation des tapis rotateurs.
        Entrees : `robot` (`Robot`), `tapis_visites` (`set[tuple[int, int]]`).
        Sorties : rien (`None`).
        Pré-requis : `robot` doit être positionné dans les limites du plateau.
        """
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

    def _faire_avancer_les_tapis(self):
        """
        Role : aucun
        Entrees : aucune
        Sorties : aucune
        Pré-requis : aucun
        """
        robots_sur_tapis = [
            (
                robot,
                (robot.x, robot.y),
                self.cases[robot.y][robot.x].direction_tapis(),
                self.cases[robot.y][robot.x].rotation,
            )
            for robot in self.robots
            if not robot.est_detruit
            and est_tapis(self.cases[robot.y][robot.x].type_case)
        ]
        for robot, position, direction, rotation in robots_sur_tapis:
            if robot.est_detruit or (robot.x, robot.y) != position:
                continue
            if rotation is not None:
                robot.orientation = self._orientation_apres_rotation(
                    robot.orientation
                )
            self._avancer(robot, direction, set())

    def _orientation_apres_rotation(self, orientation):
        """
        Role : applique le sens de rotation indiqué par la flèche du tapis rotateur.
        Entrees : `orientation` (`Direction`).
        Sorties : nouvelle orientation (`Direction`).
        Pré-requis : `orientation` doit être une valeur de `Direction`.
        """
        from entites.direction import tourner_gauche
        return tourner_gauche(orientation)

    def _capturer_drapeau(self, robot: Robot) -> None:
        """
        Role : attribue le drapeau à l'équipe du robot.
        Entrees : `robot` (`Robot`).
        Sorties : rien (`None`).
        Pré-requis : les coordonnées des drapeaux doivent être valides.
        """
        for drapeau, x, y in self.drapeaux:
            if (robot.x, robot.y) == (x, y):
                drapeau.couleur = robot.couleur
                drapeau.equipe_capture = robot.couleur

    def _tirer(self, robot):
        """
        Role : suit la ligne de tir selon l'orientation du robot jusqu'à un mur, un bord ou un robot.
        Entrees : `robot` (`Robot`).
        Sorties : cible touchée (`Robot`) ou `None`.
        Pré-requis : `robot` doit être actif et orienté correctement.
        """
        x, y = robot.x, robot.y
        while self._dans_plateau(x + robot.orientation.value[0], y + robot.orientation.value[1]):
            if not self._passage_possible(x, y, robot.orientation):
                return None
            x += robot.orientation.value[0]
            y += robot.orientation.value[1]
            cible = self._robot_a(x, y)
            if cible is not None:
                if cible.couleur != robot.couleur:
                    if self.tir_callback is not None:
                        self.tir_callback(robot, cible)
                    cible.recoit_degats(1 + robot.bonus_degats)
                    robot.bonus_degats = 0
                    return cible
                return None
        return None

    def _faire_tirer_ennemis_sur(self, cible):
        """
        Role : fait tirer chaque ennemi actif dont la cible est le premier robot visible dans son orientation.
        Entrees : `cible` (`Robot`).
        Sorties : rien (`None`).
        Pré-requis : `cible` doit être un robot actif présent sur le plateau.
        """
        for tireur in self.robots:
            if tireur is cible or tireur.est_detruit:
                continue
            if tireur.couleur == cible.couleur:
                continue
            if self._premier_robot_visible(tireur) is cible:
                self._tirer(tireur)

    def _premier_robot_visible(self, tireur):
        """
        Role : avance dans la ligne de tir jusqu'à un mur, un bord ou le premier robot rencontré.
        Entrees : `tireur` (`Robot`).
        Sorties : premier robot visible (`Robot`) ou `None`.
        Pré-requis : `tireur` doit avoir une orientation valide.
        """
        x, y = tireur.x, tireur.y
        while self._dans_plateau(
            x + tireur.orientation.value[0],
            y + tireur.orientation.value[1],
        ):
            if not self._passage_possible(x, y, tireur.orientation):
                return None
            x += tireur.orientation.value[0]
            y += tireur.orientation.value[1]
            robot = self._robot_a(x, y)
            if robot is not None:
                return robot
        return None

    def _passage_possible(self, x: int, y: int, direction: Direction) -> bool:
        """
        Role : contrôle les murs de la case de départ et de la case cible.
        Entrees : `x` (`int`), `y` (`int`), `direction` (`Direction`).
        Sorties : passage libre ou non (`bool`).
        Pré-requis : `(x, y)` doit être une position du plateau.
        """
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
        """
        Role : compare les coordonnées aux dimensions de la partie.
        Entrees : `x` (`int`), `y` (`int`).
        Sorties : position valide ou non (`bool`).
        Pré-requis : les dimensions doivent être positives.
        """
        return 0 <= x < self.largeur and 0 <= y < self.hauteur

    def _robot_a(self, x, y):
        """
        Role : parcourt les robots et ignore ceux qui sont détruits.
        Entrees : `x` (`int`), `y` (`int`).
        Sorties : robot trouvé (`Robot`) ou `None`.
        Pré-requis : aucun.
        """
        return next((r for r in self.robots if not r.est_detruit and (r.x, r.y) == (x, y)), None)
