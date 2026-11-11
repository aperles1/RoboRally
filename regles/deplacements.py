"""
Auteur : Perles Alexis
Date de dernière modification : 10/11/2026
Contenu : Fonctions de déplacement et de tapis du jeu.
"""

from entites.direction import Direction, tourner_gauche


def avancer(jeu, robot, direction, tapis_visites):
    """
    Role : deplace un robot et applique sa case d'arrivee.
    Entrees : jeu (Jeu) : partie ; robot (Robot) : robot ; direction (Direction) : direction ; tapis_visites (set) : cases visitees
    Sorties : bool : vrai si le déplacement est effectué
    Pré-requis : robot appartient à jeu
    """
    if robot.est_detruit or not jeu._passage_possible(robot.x, robot.y, direction):
        return False
    cible = jeu._robot_a(robot.x + direction.value[0], robot.y + direction.value[1])
    if cible is not None and not pousser(jeu, cible, direction, set()):
        return False
    if jeu._robot_a(robot.x + direction.value[0], robot.y + direction.value[1]) is not None:
        return False
    deplacer(jeu, robot, direction)
    jeu._effet_case(robot, tapis_visites)
    return True


def pousser(jeu, robot, direction, visites):
    """
    Role : pousse une chaine de robots.
    Entrees : jeu (Jeu) : partie ; robot (Robot) : robot a pousser ; direction (Direction) : direction ; visites (set) : robots visites
    Sorties : bool : vrai si la poussee est possible
    Pré-requis : robot est actif
    """
    if id(robot) in visites or not jeu._passage_possible(robot.x, robot.y, direction):
        return False
    visites.add(id(robot))
    cible = jeu._robot_a(robot.x + direction.value[0], robot.y + direction.value[1])
    if cible is not None and not pousser(jeu, cible, direction, visites):
        return False
    if jeu._robot_a(robot.x + direction.value[0], robot.y + direction.value[1]) is not None:
        return False
    deplacer(jeu, robot, direction)
    jeu._effet_case(robot, set())
    return True


def deplacer(jeu, robot, direction):
    """
    Role : deplace reellement un robot.
    Entrees : jeu (Jeu) : partie ; robot (Robot) : robot ; direction (Direction) : direction
    Sorties : bool : vrai si le déplacement est effectué
    Pré-requis : la case cible est libre
    """
    nouvelle = (robot.x + direction.value[0], robot.y + direction.value[1])
    occupant = jeu._robot_a(*nouvelle)
    if occupant is not None and occupant is not robot:
        return False
    robot.deplacer(direction)
    robot.positions_recentes.append((robot.x, robot.y))
    del robot.positions_recentes[:-6]
    if jeu.animation_callback is not None:
        jeu.animation_callback()
    jeu._faire_tirer_ennemis_sur(robot)
    return True


def faire_avancer_les_tapis(jeu):
    """
    Role : fait avancer chaque robot sur son tapis.
    Entrees : jeu (Jeu) : partie
    Sorties : aucune
    Pré-requis : le plateau contient des cases valides
    """
    robots = [
        (robot, (robot.x, robot.y), jeu.cases[robot.y][robot.x].direction_tapis(),
         jeu.cases[robot.y][robot.x].rotation)
        for robot in jeu.robots
        if not robot.est_detruit and jeu.cases[robot.y][robot.x].est_tapis()
    ]
    for robot, position, direction, rotation in robots:
        if robot.est_detruit or (robot.x, robot.y) != position:
            continue
        if rotation is not None:
            robot.orientation = tourner_gauche(robot.orientation)
        avancer(jeu, robot, direction, set())
