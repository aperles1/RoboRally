"""
Auteur : Perles Alexis
Date de dernière modification : 10/11/2026
Contenu : Fonctions de tir et de visibilité du jeu.
"""


def tirer(jeu, robot):
    """
    Role : tire sur le premier adversaire visible.
    Entrees : jeu (Jeu) : partie ; robot (Robot) : tireur
    Sorties : Robot ou None : cible touchee
    Pré-requis : robot est actif
    """
    x, y = robot.x, robot.y
    while jeu._dans_plateau(x + robot.orientation.value[0], y + robot.orientation.value[1]):
        if not jeu._passage_possible(x, y, robot.orientation):
            return None
        x += robot.orientation.value[0]
        y += robot.orientation.value[1]
        cible = jeu._robot_a(x, y)
        if cible is not None:
            if cible.couleur == robot.couleur:
                return None
            if jeu.tir_callback is not None:
                jeu.tir_callback(robot, cible)
            cible.recoit_degats(1 + robot.bonus_degats)
            robot.bonus_degats = 0
            return cible
    return None


def premier_robot_visible(jeu, tireur):
    """
    Role : recherche le premier robot visible dans une direction.
    Entrees : jeu (Jeu) : partie ; tireur (Robot) : robot observateur
    Sorties : Robot ou None : premier robot visible
    Pré-requis : tireur possède une orientation valide
    """
    x, y = tireur.x, tireur.y
    while jeu._dans_plateau(x + tireur.orientation.value[0], y + tireur.orientation.value[1]):
        if not jeu._passage_possible(x, y, tireur.orientation):
            return None
        x += tireur.orientation.value[0]
        y += tireur.orientation.value[1]
        robot = jeu._robot_a(x, y)
        if robot is not None:
            return robot
    return None


def faire_tirer_ennemis_sur(jeu, cible):
    """
    Role : fait tirer les ennemis qui voient une cible.
    Entrees : jeu (Jeu) : partie ; cible (Robot) : robot cible
    Sorties : aucune
    Pré-requis : cible appartient à jeu
    """
    for tireur in jeu.robots:
        if tireur is cible or tireur.est_detruit or tireur.couleur == cible.couleur:
            continue
        if premier_robot_visible(jeu, tireur) is cible:
            tirer(jeu, tireur)
