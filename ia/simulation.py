"""
Auteur : Perles Alexis
Date de dernière modification : 10/11/2026
Contenu : Simule les actions et recherche les chemins de l'oracle.
"""

from collections import deque

from entites.direction import ActionCarte, Direction, tourner_droite, tourner_gauche
from entites.type_case import TypeCase, est_tapis


ACTIONS = (
    ActionCarte.AVANCER,
    ActionCarte.TOURNER_DROITE,
    ActionCarte.TOURNER_GAUCHE,
)


class Oracle:
    def __init__(self):
        """
        Role : initialise le cache de l’oracle.
        Entrees : aucune
        Sorties : aucune
        Pré-requis : aucun
        """
        self.memoire = {}
        self.calculs = 0
        self.reutilisations = 0

    def combinaison(self, jeu, robot, maximum=40):
        """
        Role : calcule une combinaison d’actions vers l’objectif.
        Entrees : jeu (Jeu), robot (Robot), maximum (int)
        Sorties : liste d’actions
        Pré-requis : le robot doit appartenir au jeu
        """
        cible = objectif(jeu, robot)
        if cible is None:
            return []

        cle = (
            _signature_carte(jeu),
            robot.couleur,
            robot.x,
            robot.y,
            robot.orientation,
            cible,
            maximum,
        )
        if cle in self.memoire:
            self.reutilisations += 1
            return list(self.memoire[cle])

        self.calculs += 1
        chemin = _chercher_combinaison(jeu, robot, cible, maximum)
        self.memoire[cle] = tuple(chemin)
        return list(chemin)

    def vider(self):
        """
        Role : vide le cache et réinitialise les statistiques.
        Entrees : aucune
        Sorties : aucune
        Pré-requis : aucun
        """
        self.memoire.clear()
        self.calculs = 0
        self.reutilisations = 0

    def statistiques(self):
        """
        Role : retourne les statistiques du cache.
        Entrees : aucune
        Sorties : dictionnaire de statistiques
        Pré-requis : aucun
        """
        return {
            "chemins_calcules": self.calculs,
            "chemins_reutilises": self.reutilisations,
            "chemins_memorises": len(self.memoire),
        }


ORACLE = Oracle()


def objectif(jeu, robot):
    """
    Role : détermine le drapeau adverse le plus proche.
    Entrees : jeu (Jeu), robot (Robot)
    Sorties : position ou aucune
    Pré-requis : le jeu doit fournir ses drapeaux
    """
    drapeaux_adverses = [
        (x, y)
        for drapeau, x, y in jeu.drapeaux
        if drapeau.couleur_origine != robot.couleur
        and drapeau.equipe_capture != robot.couleur
    ]
    if not drapeaux_adverses:
        return None
    return min(drapeaux_adverses, key=lambda position: distance(robot, position))


def combinaison(jeu, robot, maximum=40):
    """
    Role : calcule une combinaison d’actions vers l’objectif.
    Entrees : jeu (Jeu), robot (Robot), maximum (int)
    Sorties : liste d’actions
    Pré-requis : le robot doit appartenir au jeu
    """
    cible = objectif(jeu, robot)
    if cible is None:
        return []
    return ORACLE.combinaison(jeu, robot, maximum)


def _chercher_combinaison(jeu, robot, cible, maximum):
    """
    Role : recherche une combinaison d’actions.
    Entrees : jeu (Jeu), robot (Robot), cible (position), maximum (int)
    Sorties : liste d’actions
    Pré-requis : la cible doit être une position du plateau
    """
    resultat = _chercher_bfs(
        jeu, (robot.x, robot.y, robot.orientation), cible, maximum, True
    )
    return resultat or []


def prochaine_action(jeu, robot):
    """
    Role : retourne la première action vers l’objectif.
    Entrees : jeu (Jeu), robot (Robot)
    Sorties : action ou aucune
    Pré-requis : le robot doit appartenir au jeu
    """
    actions = combinaison(jeu, robot)
    return actions[0] if actions else None


def distance(robot, position):
    """
    Role : calcule la distance de Manhattan.
    Entrees : robot (Robot), position (tuple)
    Sorties : entier
    Pré-requis : la position doit contenir deux coordonnées
    """
    return abs(robot.x - position[0]) + abs(robot.y - position[1])


def distance_actions(jeu, robot, cible, position=None, orientation=None):
    """
    Role : calcule le nombre minimal d’actions vers une cible.
    Entrees : jeu (Jeu), robot (Robot), cible (position), position (tuple) ou aucune, orientation (Direction) ou aucune
    Sorties : entier ou infini
    Pré-requis : la cible doit être accessible au moteur de recherche
    """
    depart_position = (robot.x, robot.y) if position is None else position
    depart = (
        depart_position[0],
        depart_position[1],
        robot.orientation if orientation is None else orientation,
    )
    if jeu.signature_plateau is None:
        jeu.signature_plateau = _signature_carte(jeu)
    cle = (jeu.signature_plateau, depart[0], depart[1], depart[2], cible)
    if cle in jeu.distance_actions_cache:
        return jeu.distance_actions_cache[cle]
    resultat = _chercher_bfs(jeu, depart, cible, 1000, False)
    distance = len(resultat) if resultat is not None else float("inf")
    jeu.distance_actions_cache[cle] = distance
    return distance


def _chercher_bfs(jeu, depart, cible, maximum, retourner_actions):
    """
    Role : cherche un chemin minimal dans les etats du robot.
    Entrees : jeu (Jeu) : partie ; depart (tuple) : etat initial ; cible (tuple) : position cible ; maximum (int) : profondeur maximale ; retourner_actions (bool) : format de sortie
    Sorties : list ou None : chemin trouve
    Pré-requis : depart contient x, y et orientation
    """
    # Chaque état mémorise la position, l'orientation et le chemin parcouru.
    # BFS garantit le plus petit nombre d'actions lorsque chaque action coûte 1.
    file = deque([(depart, [])])
    visites = {depart}
    while file:
        etat, actions = file.popleft()
        if etat[:2] == cible:
            return actions if retourner_actions else actions
        if len(actions) == maximum:
            continue
        for action in ACTIONS:
            # On simule avant d'ajouter l'état : un trou, un mur ou une sortie
            # du plateau ne doit jamais entrer dans les candidats.
            suivant = _simuler(jeu, etat[0], etat[1], etat[2], action)
            if suivant is None or suivant in visites:
                continue
            visites.add(suivant)
            file.append((suivant, actions + [action]))
    return None


def _simuler(jeu, x, y, orientation, action):
    """
    Role : simule une action du robot.
    Entrees : jeu (Jeu), x (int), y (int), orientation (Direction), action (ActionCarte)
    Sorties : état ou aucune
    Pré-requis : la position et l’action doivent être valides
    """
    if action == ActionCarte.TOURNER_DROITE:
        return x, y, tourner_droite(orientation)
    if action == ActionCarte.TOURNER_GAUCHE:
        return x, y, tourner_gauche(orientation)

    suivant = (x + orientation.value[0], y + orientation.value[1])
    if (
        not jeu.dans_plateau(*suivant)
        or not jeu.passage_possible(x, y, orientation)
    ):
        return None
    suivant, orientation = _suivre_tapis(jeu, suivant[0], suivant[1], orientation)
    if suivant is None:
        return None
    return suivant[0], suivant[1], orientation


def _suivre_tapis(jeu, x, y, orientation):
    """
    Role : suit les tapis roulants depuis une position.
    Entrees : jeu (Jeu), x (int), y (int), orientation (Direction)
    Sorties : position et orientation ou aucune
    Pré-requis : la position doit appartenir au plateau
    """
    visites = set()
    while jeu.dans_plateau(x, y) and (x, y) not in visites:
        visites.add((x, y))
        case = jeu.cases[y][x]
        if case.type_case == TypeCase.TROU:
            return None, orientation
        if not est_tapis(case.type_case):
            return (x, y), orientation
        direction = case.direction_tapis()
        if not jeu.passage_possible(x, y, direction):
            return None, orientation
        if case.rotation is not None:
            orientation = jeu._orientation_apres_rotation(orientation)
        x += direction.value[0]
        y += direction.value[1]
    return None, orientation


def _mouvement_dangereux(jeu, x, y):
    """
    Role : indique si un déplacement mène à un trou.
    Entrees : jeu (Jeu), x (int), y (int)
    Sorties : booléen
    Pré-requis : la position doit appartenir au plateau
    """
    visites = set()
    while jeu.dans_plateau(x, y) and (x, y) not in visites:
        visites.add((x, y))
        case = jeu.cases[y][x]
        if case.type_case == TypeCase.TROU:
            return True
        if not est_tapis(case.type_case):
            return False
        tapis = case.direction_tapis()
        x += tapis.value[0]
        y += tapis.value[1]
    return False


def _signature_carte(jeu):
    """
    Role : aucun
    Entrees : aucune
    Sorties : aucune
    Pré-requis : aucun
    """
    return tuple(
        (
            case.type_case.value,
            tuple(direction.name for direction in case.murs),
            case.rotation,
        )
        for ligne in jeu.cases
        for case in ligne
    )
