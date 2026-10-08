"""
Auteur : Perles Alexis
Date de dernière modification : 04/10/2026
Contenu : Extrait et transforme l'état du jeu en caractéristiques numériques.
"""

from Entitées.TypeCase import TypeCase


NOMS_CARACTERISTIQUES = (
    "mouvement_possible",
    "variation_distance_reparation",
    "variation_distance_bonus",
    "variation_distance_drapeau",
    "arrivee_reparation",
    "arrivee_bonus",
    "collision_allie",
    "peut_tirer",
    "est_vise",
    "position_precedente",
    "reste_sur_place",
    "vitesse_carte",
)


def distance_minimale(x, y, positions):
    """Retourne la distance de Manhattan minimale vers des positions.

    - Description : compare la position fournie à chaque position cible.
    - Prérequis : `positions` doit contenir des couples de coordonnées.
    - Arguments : `x` (`int`), `y` (`int`), `positions` (`list[tuple[int, int]]`).
    - Retourne : distance minimale (`float`), ou `0.0` si la liste est vide.
    """
    if not positions:
        return 0.0
    return float(min(abs(position_x - x) + abs(position_y - y)
                     for position_x, position_y in positions))


def objectifs_robot(jeu, robot):
    """Retourne les drapeaux ennemis encore prioritaires pour le robot.

    - Description : ignore les drapeaux déjà capturés et ceux qu'un allié
      peut atteindre plus rapidement.
    - Prérequis : `jeu` doit contenir des drapeaux et des robots cohérents.
    - Arguments : `jeu` (`Jeu`), `robot` (`Robot`).
    - Retourne : coordonnées des objectifs (`list[tuple[int, int]]`).
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
    """Vérifie si un allié est plus proche d'un drapeau.

    - Description : compare la distance du robot à celle de chaque allié actif.
    - Prérequis : `position_drapeau` doit contenir deux coordonnées.
    - Arguments : `jeu` (`Jeu`), `robot` (`Robot`),
      `position_drapeau` (`tuple[int, int]`).
    - Retourne : présence d'un allié plus proche (`bool`).
    """
    distance_robot = abs(position_drapeau[0] - robot.x) + abs(position_drapeau[1] - robot.y)
    return any(
        autre is not robot
        and not autre.est_detruit
        and autre.couleur == robot.couleur
        and abs(position_drapeau[0] - autre.x) + abs(position_drapeau[1] - autre.y)
        < distance_robot
        for autre in jeu.robots
    )


def destination_apres_tapis(jeu, x, y):
    """Suit les tapis roulants jusqu'à une case stable ou une boucle.

    - Description : simule les déplacements successifs des tapis sans modifier
      la position réelle du robot.
    - Prérequis : `(x, y)` doit être une position du plateau ou une position
      adjacente à celui-ci.
    - Arguments : `jeu` (`Jeu`), `x` (`int`), `y` (`int`).
    - Retourne : destination finale (`tuple[int, int]`).
    """
    depart = (x, y)
    visites = set()
    while jeu._dans_plateau(x, y) and (x, y) not in visites:
        visites.add((x, y))
        case = jeu.cases[y][x]
        if case.type_case == TypeCase.TROU or not case.type_case.est_tapis:
            return x, y
        direction = case.direction_tapis()
        suivant = (x + direction.value[0], y + direction.value[1])
        if not jeu._dans_plateau(*suivant) or not jeu._passage_possible(x, y, direction):
            return x, y
        x, y = suivant
    return depart if (x, y) in visites else (x, y)


def peut_tirer(jeu, position, direction, couleur):
    """Vérifie si une position permet de toucher un ennemi.

    - Description : suit la ligne de tir jusqu'au premier robot rencontré.
    - Prérequis : `position` et `direction` doivent être valides.
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


def ligne_de_tir_libre(jeu, robot, position):
    """Vérifie qu'aucun mur ne bloque une ligne de tir.

    - Description : avance de la position du robot jusqu'à la cible.
    - Prérequis : la cible doit être alignée avec l'orientation du robot.
    - Arguments : `jeu` (`Jeu`), `robot` (`Robot`),
      `position` (`tuple[int, int]`).
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


def ennemi_vise_case(jeu, position, couleur):
    """Vérifie si un ennemi peut tirer sur une position.

    - Description : recherche un ennemi aligné dont la ligne de tir est libre.
    - Prérequis : `position` doit appartenir au plateau.
    - Arguments : `jeu` (`Jeu`), `position` (`tuple[int, int]`),
      `couleur` (`str`).
    - Retourne : position menacée ou non (`bool`).
    """
    x, y = position
    for ennemi in jeu.robots:
        if ennemi.est_detruit or ennemi.couleur == couleur:
            continue
        dx, dy = ennemi.orientation.value
        distance_x, distance_y = x - ennemi.x, y - ennemi.y
        aligne = (dx and distance_y == 0 and distance_x * dx > 0) or (
            dy and distance_x == 0 and distance_y * dy > 0
        )
        if aligne and ligne_de_tir_libre(jeu, ennemi, position):
            return True
    return False


def extraire_caracteristiques(jeu, robot, direction, vitesse=0):
    """Transforme l'état du jeu et une action en vecteur numérique.

    - Description : calcule les indicateurs utilisés par le perceptron pour
      évaluer une direction et la vitesse de sa carte.
    - Prérequis : `robot` doit appartenir à `jeu` et `direction` être valide.
    - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `direction` (`Direction`),
      `vitesse` (`int`, valeur par défaut : `0`).
    - Retourne : vecteur des caractéristiques (`list[float]`).
    """
    mouvement_possible = direction_possible(jeu, robot, direction)
    if not mouvement_possible:
        return [-1.0] + [0.0] * (len(NOMS_CARACTERISTIQUES) - 1)

    nouvelle_position = destination_apres_tapis(
        jeu, robot.x + direction.value[0], robot.y + direction.value[1]
    )
    reparations = [
        (x, y) for y, ligne in enumerate(jeu.cases)
        for x, case in enumerate(ligne) if case.type_case == TypeCase.REPARATION
    ]
    bonus = [
        (x, y) for y, ligne in enumerate(jeu.cases)
        for x, case in enumerate(ligne) if case.type_case == TypeCase.BONUS
    ]
    objectifs = objectifs_robot(jeu, robot)
    arrivee = jeu.cases[nouvelle_position[1]][nouvelle_position[0]]
    return [
        1.0,
        distance_minimale(robot.x, robot.y, reparations)
        - distance_minimale(*nouvelle_position, reparations) if robot.pv < 3 else 0.0,
        distance_minimale(robot.x, robot.y, bonus)
        - distance_minimale(*nouvelle_position, bonus) if robot.pv >= 3 else 0.0,
        distance_minimale(robot.x, robot.y, objectifs)
        - distance_minimale(*nouvelle_position, objectifs),
        float(arrivee.type_case == TypeCase.REPARATION and robot.pv < 3),
        float(arrivee.type_case == TypeCase.BONUS),
        float(any(
            autre is not robot and not autre.est_detruit
            and autre.couleur == robot.couleur
            and (autre.x, autre.y) == nouvelle_position
            for autre in jeu.robots
        )),
        float(peut_tirer(jeu, nouvelle_position, direction, robot.couleur)),
        float(ennemi_vise_case(jeu, nouvelle_position, robot.couleur)),
        float(nouvelle_position in robot.positions_precedentes),
        float(nouvelle_position == (robot.x, robot.y)),
        float(vitesse) / 10.0,
    ]


def direction_possible(jeu, robot, direction):
    """Vérifie qu'une direction peut être empruntée sans tomber.

    - Description : contrôle les limites, les murs et le trajet des tapis.
    - Prérequis : `robot` doit être positionné sur le plateau.
    - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `direction` (`Direction`).
    - Retourne : déplacement possible ou non (`bool`).
    """
    x = robot.x + direction.value[0]
    y = robot.y + direction.value[1]
    return (
        jeu._dans_plateau(x, y)
        and jeu._passage_possible(robot.x, robot.y, direction)
        and not jeu.deplacement_mene_au_trou(robot, direction)
    )
