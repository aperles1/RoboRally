"""
Auteur : Perles Alexis
Date de dernière modification : 30/09/2026
Contenu : Contient l'oracle et le contrôleur de décision des robots.
"""

"""IA à règles pour contrôler les robots de RoboRally."""

from Direction import Direction
from TypeCase import TypeCase
from Carte import Carte

def score_oracle(jeu, robot, direction):
    """Note un mouvement selon les règles et objectifs du jeu.

    - Description : favorise les objectifs, bonus et tirs sûrs, et pénalise les dangers.
    - Prérequis : `robot` doit être positionné dans `jeu`.
    - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `direction` (`Direction`).
    - Retourne : note du mouvement (`float`).
    """
    if not ControleurRobot._direction_possible(jeu, robot, direction):
        return -1000.0

    dx, dy = direction.value
    position_initiale = (robot.x, robot.y)
    nouvelle_position = destination_apres_tapis(
        jeu, robot.x + dx, robot.y + dy
    )
    if not jeu._dans_plateau(*nouvelle_position):
        return -1000.0
    score = 0.0

    # Un robot blessé cherche d'abord une réparation ; les bonus restent
    # intéressants, mais leur priorité est plus faible qu'une guérison.
    reparations = []
    bonus = []
    for y, ligne in enumerate(jeu.cases):
        for x, case in enumerate(ligne):
            if case.type_case == TypeCase.REPARATION:
                reparations.append((x, y))
            elif case.type_case == TypeCase.BONUS:
                bonus.append((x, y))

    if robot.pv < 3 and reparations:
        distance_actuelle = distance_minimale(robot.x, robot.y, reparations)
        distance_apres_deplacement = distance_minimale(
            nouvelle_position[0], nouvelle_position[1], reparations
        )
        score += (distance_actuelle - distance_apres_deplacement) * 20.0
    elif bonus:
        distance_actuelle = distance_minimale(robot.x, robot.y, bonus)
        distance_apres_deplacement = distance_minimale(
            nouvelle_position[0], nouvelle_position[1], bonus
        )
        score += (distance_actuelle - distance_apres_deplacement) * 3.0

    drapeaux = objectifs_robot(jeu, robot)
    if drapeaux:
        ancienne_distance = distance_minimale(robot.x, robot.y, drapeaux)
        nouvelle_distance = distance_minimale(
            nouvelle_position[0], nouvelle_position[1], drapeaux
        )
        score += (ancienne_distance - nouvelle_distance) * 10.0

    case = jeu.cases[nouvelle_position[1]][nouvelle_position[0]]
    if case.type_case == TypeCase.REPARATION and robot.pv < 3:
        score += 12.0
    elif case.type_case == TypeCase.BONUS:
        score += 6.0

    # Un allié occupe la case et empêche le déplacement sur cette position.
    for autre in jeu.robots:
        if autre is robot or autre.est_detruit:
            continue
        distance = abs(autre.x - nouvelle_position[0]) + abs(autre.y - nouvelle_position[1])
        if autre.couleur == robot.couleur:
            if distance == 0:
                score -= 100.0
        # La proximité d'un ennemi n'est pas une récompense : seul un tir
        # possible et sans mur rend cette position intéressante.

    if peut_tirer(jeu, nouvelle_position, direction, robot.couleur):
        score += 12.0
    if ennemi_vise_case(jeu, nouvelle_position, robot.couleur):
        score -= 18.0

    if nouvelle_position in robot.positions_precedentes:
        score -= 18.0
    if nouvelle_position == position_initiale:
        score -= 30.0

    return score


def distance_minimale(x, y, positions):
    """Retourne la plus petite distance de Manhattan vers une liste de positions.

    - Description : compare chaque position avec les coordonnées fournies.
    - Prérequis : `positions` doit contenir au moins une position.
    - Arguments : `x` (`int`), `y` (`int`), `positions` (`list[tuple[int, int]]`).
    - Retourne : distance minimale (`int`).
    """
    distance_minimum = None
    for position_x, position_y in positions:
        distance = abs(position_x - x) + abs(position_y - y)
        if distance_minimum is None or distance < distance_minimum:
            distance_minimum = distance
    return distance_minimum


def objectifs_robot(jeu, robot):
    """Retourne les drapeaux que ce robot doit prendre en priorité.

    - Description : conserve les drapeaux ennemis non capturés par l'équipe
      et ignore ceux qu'un allié peut atteindre plus rapidement.
    - Prérequis : les drapeaux doivent avoir `couleur_origine` et
      `equipe_capture`; les robots doivent avoir des coordonnées valides.
    - Arguments : `jeu` (`Jeu`), `robot` (`Robot`).
    - Retourne : positions des objectifs prioritaires (`list[tuple[int, int]]`).
    """
    objectifs = []
    for drapeau, x, y in jeu.drapeaux:
        if (
            drapeau.couleur_origine != robot.couleur
            and drapeau.equipe_capture != robot.couleur
            and not allie_plus_proche_du_drapeau(jeu, robot, (x, y))
        ):
            objectifs.append((x, y))
    return objectifs


def allie_plus_proche_du_drapeau(jeu, robot, position_drapeau):
    """Vérifie si un allié est plus proche d'un drapeau que le robot.

    - Description : compare la distance de Manhattan du robot avec celle de
      chaque allié actif vers le même drapeau.
    - Prérequis : `position_drapeau` doit contenir des coordonnées du plateau.
    - Arguments : `jeu` (`Jeu`), `robot` (`Robot`),
      `position_drapeau` (`tuple[int, int]`).
    - Retourne : présence d'un allié strictement plus proche (`bool`).
    """
    drapeau_x, drapeau_y = position_drapeau
    distance_robot = abs(drapeau_x - robot.x) + abs(drapeau_y - robot.y)

    for autre in jeu.robots:
        if autre is robot or autre.est_detruit:
            continue
        if autre.couleur != robot.couleur:
            continue

        distance_allie = abs(drapeau_x - autre.x) + abs(drapeau_y - autre.y)
        if distance_allie < distance_robot:
            return True

    return False


def destination_apres_tapis(jeu, x, y):
    """Calcule la destination après les tapis roulants successifs.

    - Description : suit les tapis jusqu'à une case stable, un bord ou une boucle.
    - Prérequis : `jeu` doit fournir les cases et les règles de passage.
    - Arguments : `jeu` (`Jeu`), `x` (`int`), `y` (`int`).
    - Retourne : coordonnées finales (`tuple[int, int]`).
    """
    depart = (x, y)
    visites = set()
    while jeu._dans_plateau(x, y) and (x, y) not in visites:
        visites.add((x, y))
        case = jeu.cases[y][x]
        if case.type_case == TypeCase.TROU or not case.type_case.est_tapis:
            return x, y
        direction = case.direction_tapis()
        suivant_x = x + direction.value[0]
        suivant_y = y + direction.value[1]
        if not jeu._dans_plateau(suivant_x, suivant_y):
            return x, y
        if not jeu._passage_possible(x, y, direction):
            return x, y
        x, y = suivant_x, suivant_y
    return depart if (x, y) in visites else (x, y)


def peut_tirer(jeu, position, direction, couleur):
    """Vérifie si une position permet de tirer sur un ennemi.

    - Description : parcourt la ligne de tir jusqu'au premier robot rencontré.
    - Prérequis : `position` doit être une coordonnée du plateau.
    - Arguments : `jeu` (`Jeu`), `position` (`tuple[int, int]`),
      `direction` (`Direction`), `couleur` (`str`).
    - Retourne : présence d'une cible ennemie (`bool`).
    """
    x, y = position
    while jeu._dans_plateau(x + direction.value[0], y + direction.value[1]):
        if not jeu._passage_possible(x, y, direction):
            return False
        x += direction.value[0]
        y += direction.value[1]
        cible = jeu._robot_a(x, y)
        if cible is not None:
            return cible.couleur != couleur
    return False


def ennemi_vise_case(jeu, position, couleur):
    """Vérifie si un ennemi peut viser une position.

    - Description : recherche un adversaire aligné et sans mur entre lui et la case.
    - Prérequis : `position` doit être une coordonnée du plateau.
    - Arguments : `jeu` (`Jeu`), `position` (`tuple[int, int]`), `couleur` (`str`).
    - Retourne : case menacée ou non (`bool`).
    """
    x, y = position
    for ennemi in jeu.robots:
        if ennemi.est_detruit or ennemi.couleur == couleur:
            continue
        dx, dy = ennemi.orientation.value
        distance_x = x - ennemi.x
        distance_y = y - ennemi.y
        if (dx, dy) == (0, 0):
            continue
        if dx and distance_y == 0 and distance_x * dx > 0:
            return ligne_de_tir_libre(jeu, ennemi, position)
        if dy and distance_x == 0 and distance_y * dy > 0:
            return ligne_de_tir_libre(jeu, ennemi, position)
    return False


def ligne_de_tir_libre(jeu, robot, position):
    """Vérifie qu'aucun mur ne bloque une ligne de tir.

    - Description : avance de la position du robot jusqu'à la cible.
    - Prérequis : la cible doit être alignée avec le robot.
    - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `position` (`tuple[int, int]`).
    - Retourne : ligne libre ou non (`bool`).
    """
    x, y = robot.x, robot.y
    dx, dy = robot.orientation.value
    while (x, y) != position:
        if not jeu._passage_possible(x, y, robot.orientation):
            return False
        x += dx
        y += dy
    return True


def direction_oracle(jeu, robot):
    """Retourne la meilleure direction de déplacement selon l'oracle.

    - Description : évalue les directions de déplacement sûres et conserve la mieux notée.
    - Prérequis : `robot` doit être un robot de `jeu`.
    - Arguments : `jeu` (`Jeu`), `robot` (`Robot`).
    - Retourne : direction de déplacement recommandée (`Direction`).
    """
    meilleure_direction = robot.orientation
    meilleur_score = 0.0

    # On compare chaque direction possible sans utiliser de fonction de tri.
    for direction_deplacement in Direction:
        if ControleurRobot._direction_possible(jeu, robot, direction_deplacement):
            score = score_oracle(jeu, robot, direction_deplacement)
            if score > meilleur_score:
                meilleur_score = score
                meilleure_direction = direction_deplacement

    return meilleure_direction


class ControleurRobot:
    """Applique les règles de décision de l'intelligence artificielle."""

    def tirer_et_choisir_cartes(self, jeu, robot):
        """Tire cinq cartes et sélectionne les trois mieux notées.

        - Description : génère les cartes et choisit successivement la meilleure.
        - Prérequis : `jeu` doit fournir un générateur aléatoire.
        - Arguments : `jeu` (`Jeu`), `robot` (`Robot`).
        - Retourne : cartes retenues (`list[Carte]`).
        """
        cartes = [
            Carte.aleatoire(jeu.aleatoire)
            for _ in range(jeu.CARTES_A_TIRER)
        ]
        # Chaque passage choisit une carte, puis la retire des cartes restantes.
        cartes_choisies = []
        for _ in range(jeu.CARTES_PAR_ROBOT):
            meilleure_carte = None
            meilleur_score = None
            for carte in cartes:
                score = self.score_carte(jeu, robot, carte)
                if meilleur_score is None or score > meilleur_score:
                    meilleur_score = score
                    meilleure_carte = carte
            cartes_choisies.append(meilleure_carte)
            cartes.remove(meilleure_carte)
        return cartes_choisies

    def score_carte(self, jeu, robot, carte):
        """Note une carte selon sa vitesse et son déplacement.

        - Description : combine la vitesse de la carte et la note de l'oracle.
        - Prérequis : `carte.direction` doit être une direction valide.
        - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `carte` (`Carte`).
        - Retourne : score de la carte (`float`).
        """
        score = carte.vitesse / 10.0
        score += score_oracle(jeu, robot, carte.direction)
        return score

    def preparer_tour(self, jeu):
        """Fait choisir trois cartes à chaque robot actif.

        - Description : prépare les mains puis les installe dans la partie.
        - Prérequis : `jeu` doit accepter `installer_cartes`.
        - Arguments : `jeu` (`Jeu`).
        - Retourne : cartes installées (`dict[int, list[Carte]]`).
        """
        cartes = {
            id(robot): self.tirer_et_choisir_cartes(jeu, robot)
            for robot in jeu.robots
            if not robot.est_detruit
        }
        jeu.installer_cartes(cartes)
        return cartes

    def doit_jouer_carte(self, jeu, robot, carte):
        """Décide si une carte peut être jouée sans danger immédiat.

        - Description : vérifie la validité de la direction de la carte.
        - Prérequis : `carte.direction` doit être une direction valide.
        - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `carte` (`Carte`).
        - Retourne : carte jouable ou non (`bool`).
        """
        return self._direction_possible(jeu, robot, carte.direction)

    @staticmethod
    def _direction_possible(jeu, robot, direction):
        """Vérifie qu'une direction reste dans le plateau et évite les trous.

        - Description : contrôle les limites, les murs et le trajet des tapis.
        - Prérequis : `robot` doit être positionné sur le plateau.
        - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `direction` (`Direction`).
        - Retourne : direction sûre ou non (`bool`).
        """
        x = robot.x + direction.value[0]
        y = robot.y + direction.value[1]
        if not (0 <= x < jeu.largeur and 0 <= y < jeu.hauteur):
            return False
        if not jeu._passage_possible(robot.x, robot.y, direction):
            return False
        return not jeu.deplacement_mene_au_trou(robot, direction)
