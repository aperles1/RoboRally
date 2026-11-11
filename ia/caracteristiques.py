"""Caractéristiques simples et normalisées utilisées par le contrôleur."""

from entites.direction import ActionCarte, Direction, tourner_droite, tourner_gauche
from entites.type_case import TypeCase, est_tapis
from ia.simulation import distance_actions


NOMS_CARACTERISTIQUES = (
    "gain_distance",
    "alignement",
    "distance_actions",
    "avance",
    "tourne_droite",
    "vitesse",
    "carte_possible",
    "rotation_opposee",
    "position_deja_visee",
    "action_repetee",
    "rotation_sans_avancer",
    "gain_distance_carre",
    "alignement_carre",
    "distance_actions_carre",
    "avance_carre",
    "tourne_droite_carre",
    "vitesse_carre",
    "carte_possible_carre",
    "rotation_opposee_carre",
    "position_deja_visee_carre",
    "action_repetee_carre",
    "rotation_sans_avancer_carre",
)


def extraire_caracteristiques(
    jeu, robot, action, vitesse=0, cartes_precedentes=(), contexte=None
):
    """
    Role : calcule les valeurs normalisées utilisées par le contrôleur.
    Entrees : `jeu` (partie en cours), `robot` (robot évalué), `action` (action à évaluer), `vitesse` (vitesse de la carte), `cartes_precedentes` (actions déjà jouées), `contexte` (cibles précalculées ou `None`).
    Sorties : liste de caractéristiques normalisées (`list[float]`). `contexte` peut être préparé une fois pour chaque robot et chaque tour afin d'éviter de rechercher les ennemis, les drapeaux et l'objectif pour chaque carte de la main.
    Pré-requis : `jeu`, `robot` et `action` doivent représenter une situation de jeu valide.
    """
    contexte = contexte or preparer_contexte(jeu, robot)
    objectif = contexte["objectif"]
    position, orientation, _ = _etat_apres_action(
        jeu, robot, action
    )
    distance_avant = _distance(robot.x, robot.y, objectif)
    distance_apres = _distance(*position, objectif)
    # gain = distance avant l'action - distance après l'action.
    gain_distance = _normaliser_signe(
        distance_avant - distance_apres,
        max(1, jeu.largeur + jeu.hauteur),
    )
    alignement = _alignement(orientation, robot, position, objectif)
    distance_bfs = distance_actions(jeu, robot, objectif, position, orientation)
    distance_normalisee = (
        1.0 if distance_bfs == float("inf")
        else _normaliser(distance_bfs, max(1, jeu.largeur + jeu.hauteur))
    )
    rotations = (ActionCarte.TOURNER_DROITE, ActionCarte.TOURNER_GAUCHE)
    valeurs = (
        gain_distance,
        alignement,
        distance_normalisee,
        float(action == ActionCarte.AVANCER),
        float(action == ActionCarte.TOURNER_DROITE),
        _normaliser(vitesse, 100),
        float(_carte_possible(jeu, robot, action)),
        _rotation_opposee(cartes_precedentes, action),
        _position_deja_visee(robot, action),
        _action_repetee(robot, action),
        float(action in rotations and _rotation_sans_avancer(robot)),
    )
    valeurs = [
        max(-1.0, min(1.0, float(valeur))) for valeur in valeurs
    ]
    return valeurs + [valeur ** 2 for valeur in valeurs]


def preparer_contexte(jeu, robot):
    """
    Role : rassemble les ennemis, les drapeaux et l'objectif du robot.
    Entrees : `jeu` (partie en cours), `robot` (robot évalué).
    Sorties : contexte de décision (`dict`).
    Pré-requis : `jeu` et `robot` doivent appartenir à la partie en cours.
    """
    ennemis = [
        autre for autre in jeu.robots
        if autre is not robot
        and autre.couleur != robot.couleur
        and not autre.est_detruit
    ]
    drapeaux = [
        (x, y) for drapeau, x, y in jeu.drapeaux
        if drapeau.couleur_origine != robot.couleur
        and drapeau.equipe_capture != robot.couleur
    ]
    objectif, objectif_drapeau = _objectif(jeu, robot, drapeaux, ennemis)
    return {
        "ennemis": ennemis,
        "drapeaux": drapeaux,
        "objectif": objectif,
        "objectif_drapeau": objectif_drapeau,
    }


def _objectif(jeu, robot, drapeaux, ennemis):
    """
    Role : choisit le drapeau adverse, puis l'ennemi le plus proche.
    Entrees : `jeu` (partie en cours), `robot` (robot évalué), `drapeaux` (positions des drapeaux disponibles), `ennemis` (robots adverses).
    Sorties : cible et indicateur de cible-drapeau (`tuple`).
    Pré-requis : `robot` doit fournir ses coordonnées.
    """
    if drapeaux:
        cible = min(drapeaux, key=lambda p: _distance(robot.x, robot.y, p))
        return cible, True
    if ennemis:
        positions = [(ennemi.x, ennemi.y) for ennemi in ennemis]
        return min(positions, key=lambda p: _distance(robot.x, robot.y, p)), False
    return (robot.x, robot.y), False


def _distance(x, y, position):
    """
    Role : additionne les écarts horizontaux et verticaux.
    Entrees : `x` (`int` ou `float`), `y` (`int` ou `float`), `position` (coordonnées de destination).
    Sorties : distance de Manhattan (`int` ou `float`).
    Pré-requis : `position` doit contenir deux coordonnées numériques.
    """
    return abs(position[0] - x) + abs(position[1] - y)


def _normaliser(valeur, maximum):
    """
    Role : applique une normalisation centrée puis borne le résultat.
    Entrees : `valeur` (valeur à normaliser), `maximum` (borne de référence).
    Sorties : valeur normalisée (`float`). Formule : valeur normalisée = 2 * valeur / maximum - 1. Pour un gain signé, le résultat est ensuite borné à [-1, 1].
    Pré-requis : `maximum` doit être positif ou nul.
    """
    if maximum == 0:
        return 0.0
    return max(-1.0, min(1.0, 2 * valeur / maximum - 1))


def _normaliser_signe(valeur, maximum):
    """
    Role : rapporte une variation à une valeur maximale puis la borne.
    Entrees : `valeur` (variation à normaliser), `maximum` (borne de référence).
    Sorties : variation normalisée (`float`). Formule : variation normalisée = variation / maximum.
    Pré-requis : `maximum` doit être positif ou nul.
    """
    if maximum == 0:
        return 0.0
    return max(-1.0, min(1.0, valeur / maximum))


def _alignement(orientation, robot, position, objectif):
    """
    Role : mesure le produit scalaire de la direction du robot et du vecteur vers l'objectif.
    Entrees : `orientation` (orientation du robot), `robot` (robot évalué), `position` (position après l'action), `objectif` (coordonnées de la cible).
    Sorties : score d'alignement borné dans [-1, 1] (`float`).
    Pré-requis : `orientation.value` doit contenir deux composantes.
    """
    dx = objectif[0] - position[0]
    dy = objectif[1] - position[1]
    longueur = abs(dx) + abs(dy)
    if longueur == 0:
        return 1.0
    # u = direction du robot après l'action, v = direction de l'objectif.
    # alignement = u . v = (u_x * v_x + u_y * v_y) / ||v||_1.
    return max(-1.0, min(1.0, (
        orientation.value[0] * dx + orientation.value[1] * dy
    ) / longueur))


def _carte_possible(jeu, robot, action):
    """
    Role : accepte toujours une rotation et vérifie le déplacement.
    Entrees : `jeu` (partie en cours), `robot` (robot évalué), `action` (action à vérifier).
    Sorties : `True` si l'action est possible, sinon `False` (`bool`).
    Pré-requis : `jeu`, `robot` et `action` doivent être valides.
    """
    if action != ActionCarte.AVANCER:
        return True
    return _etat_apres_action(jeu, robot, action)[2] is False


def _etat_apres_action(jeu, robot, action):
    """
    Role : calcule la position, l'orientation et le risque de chute.
    Entrees : `jeu` (partie en cours), `robot` (robot évalué), `action` (action à simuler).
    Sorties : position, orientation et indicateur de chute (`tuple`).
    Pré-requis : `jeu` doit fournir le plateau et les règles de passage.
    """
    orientation = robot.orientation
    if action == ActionCarte.TOURNER_DROITE:
        orientation = tourner_droite(orientation)
        return (robot.x, robot.y), orientation, False
    if action == ActionCarte.TOURNER_GAUCHE:
        orientation = tourner_gauche(orientation)
        return (robot.x, robot.y), orientation, False

    if not jeu.dans_plateau(
        robot.x + orientation.value[0], robot.y + orientation.value[1]
    ) or not jeu.passage_possible(robot.x, robot.y, orientation):
        return (robot.x, robot.y), orientation, True
    x = robot.x + orientation.value[0]
    y = robot.y + orientation.value[1]
    visites = set()
    while jeu.dans_plateau(x, y) and (x, y) not in visites:
        visites.add((x, y))
        case = jeu.cases[y][x]
        if case.type_case == TypeCase.TROU:
            return (x, y), orientation, True
        if not est_tapis(case.type_case):
            return (x, y), orientation, False
        tapis = case.direction_tapis()
        if not jeu.passage_possible(x, y, tapis):
            return (x, y), orientation, True
        x += tapis.value[0]
        y += tapis.value[1]
    return (robot.x, robot.y), orientation, True


def _position_deja_visee(robot, action):
    """
    Role : compare la case d'avance aux positions récentes du robot.
    Entrees : `robot` (robot évalué), `action` (action à vérifier).
    Sorties : indicateur numérique (`float`).
    Pré-requis : `robot` doit fournir sa position, son orientation et son historique.
    """
    if action != ActionCarte.AVANCER:
        return 0.0
    position = (
        robot.x + robot.orientation.value[0],
        robot.y + robot.orientation.value[1],
    )
    return float(position in robot.positions_recentes)


def _action_repetee(robot, action):
    """
    Role : compare l'action aux deux dernières actions du robot.
    Entrees : `robot` (robot évalué), `action` (action à vérifier).
    Sorties : indicateur numérique (`float`).
    Pré-requis : `robot.actions_recentes` doit être un historique indexable.
    """
    return float(
        len(robot.actions_recentes) >= 2
        and robot.actions_recentes[-1] == action
        and robot.actions_recentes[-2] == action
    )


def _rotation_sans_avancer(robot):
    """
    Role : détecte une succession de rotations sans déplacement.
    Entrees : `robot` (robot évalué).
    Sorties : `True` si les deux actions sont des rotations, sinon `False`.
    Pré-requis : `robot.actions_recentes` doit être un historique indexable.
    """
    rotations = (ActionCarte.TOURNER_DROITE, ActionCarte.TOURNER_GAUCHE)
    return len(robot.actions_recentes) >= 2 and all(
        ancienne in rotations for ancienne in robot.actions_recentes[-2:]
    )


def _rotation_opposee(cartes_precedentes, action):
    """
    Role : compare l'action à la dernière carte précédente.
    Entrees : `cartes_precedentes` (actions déjà jouées), `action` (action à vérifier).
    Sorties : indicateur numérique (`float`).
    Pré-requis : `cartes_precedentes` doit être un itérable d'actions.
    """
    if not cartes_precedentes:
        return 0.0
    derniere = cartes_precedentes[-1]
    return float(
        (derniere == ActionCarte.TOURNER_DROITE
         and action == ActionCarte.TOURNER_GAUCHE)
        or (derniere == ActionCarte.TOURNER_GAUCHE
            and action == ActionCarte.TOURNER_DROITE)
    )


def _position_apres_action(jeu, robot, action):
    """
    Role : conserve l'interface de l'ancien helper de simulation.
    Entrees : `jeu` (partie en cours), `robot` (robot évalué), `action` (action à simuler).
    Sorties : coordonnées après l'action (`tuple[int, int]`).
    Pré-requis : `jeu`, `robot` et `action` doivent être valides.
    """
    return _etat_apres_action(jeu, robot, action)[0]
