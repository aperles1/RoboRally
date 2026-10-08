"""
Auteur : Perles Alexis
Date de dernière modification : 30/09/2026
Contenu : Contient les règles, les déplacements et les combats de RoboRally.
"""

"""Règles centrales de RoboRally.

Ce module ne connaît pas pygame : il peut donc être testé sans dépendre de
l'interface graphique.
"""

import random

from Entitées.Carte import Carte
from Entitées.Direction import Direction
from Entitées.Robot import Robot
from Entitées.TypeCase import TypeCase


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
        """Initialise une partie et prépare son premier tour.

        - Description : copie le plateau, configure le hasard et les collections de jeu.
        - Prérequis : `cases` doit représenter un plateau rectangulaire.
        - Arguments : `robots` (`list[Robot]`), `largeur` (`int`), `hauteur` (`int`),
          `cases` (`list[list[Case]]`), `graine` (`int` ou `None`).
        - Retourne : rien (`None`).
        """
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
        self.animation_callback = None
        self.tir_callback = None
        self.nouvelle_pioche()

    def nouvelle_pioche(self, cartes_par_robot=None):
        """Prépare les cartes du nouveau tour.

        - Description : tire cinq cartes aléatoires ou utilise les cartes fournies,
          puis organise les cartes en manches, une carte par robot et par manche.
        - Prérequis : les robots doivent posséder l'attribut `est_detruit`.
        - Arguments : `cartes_par_robot` (`dict[int, list[Carte]]` ou `None`).
        - Retourne : rien (`None`).
        """
        self.numero_tour += 1
        # Chaque robot reçoit cinq cartes possibles, puis n'en conserve que trois.
        self.mains = cartes_par_robot or {
            id(robot): self.aleatoire.sample(
                [
                    Carte.aleatoire(self.aleatoire)
                    for _ in range(self.CARTES_A_TIRER)
                ],
                self.CARTES_PAR_ROBOT,
            )
            for robot in self.robots if not robot.est_detruit
        }
        self.cartes_du_tour = []
        self._organiser_cartes_par_manches()

    def installer_cartes(self, cartes_par_robot):
        """Installe les cartes choisies pour le tour courant.

        - Description : associe les cartes aux robots actifs et les organise en
          manches, une carte par robot et par manche, selon la vitesse.
        - Prérequis : les clés du dictionnaire doivent être des identifiants de robots.
        - Arguments : `cartes_par_robot` (`dict[int, list[Carte]]`).
        - Retourne : rien (`None`).
        """
        self.numero_tour += 1
        self.mains = {
            id(robot): list(cartes_par_robot.get(id(robot), []))
            for robot in self.robots
            if not robot.est_detruit
        }
        self.cartes_du_tour = []
        self._organiser_cartes_par_manches()

    def _organiser_cartes_par_manches(self):
        """Construit la file d'exécution des cartes du tour.

        Chaque robot trie sa main par vitesse décroissante. La première manche
        contient donc la carte la plus rapide de chaque robot, puis les
        manches suivantes contiennent les cartes restantes dans le même ordre.
        Les cartes d'une manche sont ensuite jouées par vitesse décroissante.
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

    def carte_actuelle(self):
        """Retourne la carte prioritaire de la manche courante.

        - Description : lit le premier élément de la file des cartes du tour.
        - Prérequis : aucun.
        - Arguments : aucun.
        - Retourne : couple robot-carte (`tuple[Robot, Carte]`) ou `None`.
        """
        return self.cartes_du_tour[0] if self.cartes_du_tour else None

    def deplacement_mene_au_trou(self, robot: Robot, direction: Direction) -> bool:
        """Vérifie si un déplacement finit dans un trou.

        - Description : suit la case cible et les tapis successifs jusqu'à un arrêt.
        - Prérequis : `robot` doit être présent sur le plateau.
        - Arguments : `robot` (`Robot`), `direction` (`Direction`).
        - Retourne : déplacement dangereux ou non (`bool`).
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
            if not case.type_case.est_tapis:
                return False
            tapis_direction = case.direction_tapis()
            x += tapis_direction.value[0]
            y += tapis_direction.value[1]
            if not self._dans_plateau(x, y):
                return False
        return False

    def tableau_plateau(self):
        """Encode le plateau dans un tableau numérique exploitable par l'IA.

        - Description : transforme chaque case, robot, drapeau et mur en 16 indicateurs
          (vide, trou, bonus, réparation, tapis, robots, drapeaux et murs).
        - Prérequis : les dimensions de `cases` doivent correspondre au plateau.
        - Arguments : aucun.
        - Retourne : tableau encodé (`list[list[list[float]]]`).
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
        """Joue ou passe la carte prioritaire.

        - Description : retire la carte, déplace et fait tirer le robot si demandé,
          puis actualise la victoire.
        - Prérequis : la file des cartes doit contenir des cartes valides.
        - Arguments : `jouer` (`bool`).
        - Retourne : robot concerné (`Robot`) ou `None`.
        """
        actuelle = self.carte_actuelle()
        if actuelle is None:
            return None
        robot, carte = actuelle
        self.cartes_du_tour.pop(0)
        self.mains[id(robot)].remove(carte)
        self.derniers_deplacements = []
        if jouer and not robot.est_detruit:
            robot.orientation = carte.direction
            self._avancer(robot, carte.direction, set())
            self._tirer(robot)
        self._actualiser_victoire()
        if not self.cartes_du_tour:
            self._actualiser_victoire()
        return robot

    def _actualiser_victoire(self) -> None:
        """Détermine si une équipe a gagné.

        - Description : vérifie si tous les drapeaux ont la même couleur ou
          si les adversaires sont éliminés.
        - Prérequis : les robots et drapeaux doivent être cohérents.
        - Arguments : aucun.
        - Retourne : rien (`None`).
        """
        equipes = {robot.couleur for robot in self.robots}
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
        """Tente de déplacer un robot et de déclencher sa case d'arrivée.

        - Description : vérifie le passage, pousse un robot si nécessaire, puis avance.
        - Prérequis : `robot` doit appartenir à la partie.
        - Arguments : `robot` (`Robot`), `direction` (`Direction`),
          `tapis_visites` (`set[tuple[int, int]]`).
        - Retourne : déplacement effectué (`bool`).
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
        """Pousse récursivement une chaîne de robots.

        - Description : libère la case suivante avant de déplacer le robot courant.
        - Prérequis : `robot` doit être actif et `direction` valide.
        - Arguments : `robot` (`Robot`), `direction` (`Direction`),
          `visites` (`set[int]`).
        - Retourne : poussée effectuée (`bool`).
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
        """Déplace réellement un robot et mémorise son trajet.

        - Description : met à jour les coordonnées, l'historique et l'animation.
        - Prérequis : la nouvelle position doit être libre.
        - Arguments : `robot` (`Robot`), `direction` (`Direction`).
        - Retourne : déplacement effectué (`bool`).
        """
        ancienne = (robot.x, robot.y)
        nouvelle = (
            robot.x + direction.value[0],
            robot.y + direction.value[1],
        )
        occupant = self._robot_a(*nouvelle)
        if occupant is not None and occupant is not robot:
            return False
        robot.positions_precedentes.append(ancienne)
        del robot.positions_precedentes[:-4]
        robot.deplacer(direction)
        self.derniers_deplacements.append((robot, ancienne, (robot.x, robot.y)))
        if self.animation_callback is not None:
            self.animation_callback()
        self._faire_tirer_ennemis_sur(robot)
        return True

    def _effet_case(self, robot, tapis_visites):
        """Applique l'effet de la case atteinte.

        - Description : gère les trous, bonus, réparations, drapeaux, tapis
          et changements d'orientation des tapis rotateurs.
        - Prérequis : `robot` doit être positionné dans les limites du plateau.
        - Arguments : `robot` (`Robot`), `tapis_visites` (`set[tuple[int, int]]`).
        - Retourne : rien (`None`).
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
        if case.type_case.est_tapis and (robot.x, robot.y) not in tapis_visites:
            tapis_visites.add((robot.x, robot.y))
            if case.rotation is not None:
                robot.orientation = self._orientation_apres_rotation(
                    robot.orientation
                )
            self._avancer(robot, case.direction_tapis(), tapis_visites)

    @staticmethod
    def _orientation_apres_rotation(orientation: Direction) -> Direction:
        """Tourne l'orientation du robot de 90 degrés.

        - Description : applique le sens de rotation indiqué par la flèche
          du tapis rotateur.
        - Prérequis : `orientation` doit être une valeur de `Direction`.
        - Arguments : `orientation` (`Direction`).
        - Retourne : nouvelle orientation (`Direction`).
        """
        rotations = {
            Direction.NORD: Direction.OUEST,
            Direction.OUEST: Direction.SUD,
            Direction.SUD: Direction.EST,
            Direction.EST: Direction.NORD,
        }
        return rotations[orientation]

    def _capturer_drapeau(self, robot: Robot) -> None:
        """Capture tout drapeau situé sous le robot.

        - Description : attribue le drapeau à l'équipe du robot.
        - Prérequis : les coordonnées des drapeaux doivent être valides.
        - Arguments : `robot` (`Robot`).
        - Retourne : rien (`None`).
        """
        for drapeau, x, y in self.drapeaux:
            if (robot.x, robot.y) == (x, y):
                drapeau.couleur = robot.couleur
                drapeau.equipe_capture = robot.couleur

    def _tirer(self, robot):
        """Tire sur le premier adversaire visible dans l'orientation du robot.

        - Description : suit la ligne de tir selon l'orientation du robot jusqu'à un mur,
          un bord ou un robot.
        - Prérequis : `robot` doit être actif et orienté correctement.
        - Arguments : `robot` (`Robot`).
        - Retourne : cible touchée (`Robot`) ou `None`.
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
        """Déclenche les tirs des ennemis qui voient la cible.

        - Description : fait tirer chaque ennemi actif dont la cible est le
          premier robot visible dans son orientation.
        - Prérequis : `cible` doit être un robot actif présent sur le plateau.
        - Arguments : `cible` (`Robot`).
        - Retourne : rien (`None`).
        """
        for tireur in self.robots:
            if tireur is cible or tireur.est_detruit:
                continue
            if tireur.couleur == cible.couleur:
                continue
            if self._premier_robot_visible(tireur) is cible:
                self._tirer(tireur)

    def _premier_robot_visible(self, tireur):
        """Recherche le premier robot visible dans une orientation.

        - Description : avance dans la ligne de tir jusqu'à un mur, un bord ou
          le premier robot rencontré.
        - Prérequis : `tireur` doit avoir une orientation valide.
        - Arguments : `tireur` (`Robot`).
        - Retourne : premier robot visible (`Robot`) ou `None`.
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
        """Vérifie qu'un déplacement franchit deux bords sans mur.

        - Description : contrôle les murs de la case de départ et de la case cible.
        - Prérequis : `(x, y)` doit être une position du plateau.
        - Arguments : `x` (`int`), `y` (`int`), `direction` (`Direction`).
        - Retourne : passage libre ou non (`bool`).
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
        """Vérifie qu'une position appartient au plateau.

        - Description : compare les coordonnées aux dimensions de la partie.
        - Prérequis : les dimensions doivent être positives.
        - Arguments : `x` (`int`), `y` (`int`).
        - Retourne : position valide ou non (`bool`).
        """
        return 0 <= x < self.largeur and 0 <= y < self.hauteur

    def _robot_a(self, x, y):
        """Recherche le robot actif placé à une position.

        - Description : parcourt les robots et ignore ceux qui sont détruits.
        - Prérequis : aucun.
        - Arguments : `x` (`int`), `y` (`int`).
        - Retourne : robot trouvé (`Robot`) ou `None`.
        """
        return next((r for r in self.robots if not r.est_detruit and (r.x, r.y) == (x, y)), None)
