"""
Auteur : Perles Alexis
Date de dernière modification : 30/09/2026
Contenu : Lance la partie et orchestre la boucle graphique pygame.
"""

"""Lancement de RoboRally avec les robots contrôlés par une IA."""

import pygame

from Drapeau import Drapeau
from Direction import Direction
from Jeu import Jeu
from Perceptron import ControleurRobot
from Plateau import (
    HAUTEUR,
    LARGEUR,
    TAILLE_PLATEAU,
    afficher_tir,
    dessiner,
    creer_images,
    creer_plateau,
)
from Robot import Robot


def creer_jeu():
    """Construit une partie avec le plateau, les robots et les drapeaux.

    - Description : assemble tous les objets nécessaires au lancement du jeu.
    - Prérequis : les constantes et classes importées doivent être disponibles.
    - Arguments : aucun.
    - Retourne : partie et murs du plateau (`tuple[Jeu, dict]`).
    """
    cases, murs = creer_plateau()
    robots = [
        Robot("Robot Bleu 1", 0, 0, Direction.EST, "bleu"),
        Robot("Robot Bleu 2", 1, 0, Direction.EST, "bleu"),
        Robot("Robot Rouge 1", 10, 11, Direction.OUEST, "rouge"),
        Robot("Robot Rouge 2", 11, 11, Direction.OUEST, "rouge"),
    ]
    jeu = Jeu(robots, TAILLE_PLATEAU, TAILLE_PLATEAU, cases)
    jeu.drapeaux = [
        (Drapeau("bleu"), 3, 1),
        (Drapeau("bleu"), 4, 4),
        (Drapeau("rouge"), 8, 10),
        (Drapeau("rouge"), 10, 9),
    ]
    return jeu, murs


def jouer_un_cycle_ia(jeu, ia):
    """Résout la prochaine carte avec l'intelligence artificielle.

    - Description : prépare un tour si nécessaire, entraîne l'IA puis joue la carte courante.
    - Prérequis : `jeu` doit être un objet `Jeu` et `ia` un objet `ControleurRobot`.
    - Arguments : `jeu` (`Jeu`), `ia` (`ControleurRobot`).
    - Retourne : rien (`None`).
    """
    if not jeu.cartes_du_tour:
        ia.preparer_tour(jeu)
    actuelle = jeu.carte_actuelle()
    if actuelle is None:
        return
    robot, carte = actuelle
    jouer = ia.doit_jouer_carte(jeu, robot, carte)
    jeu.jouer_carte_actuelle(jouer)


def main() -> None:
    """Lance la boucle graphique principale de RoboRally.

    - Description : initialise pygame, affiche le plateau et fait jouer l'IA.
    - Prérequis : pygame doit être installé et les images du projet accessibles.
    - Arguments : aucun.
    - Retourne : rien (`None`).
    """
    pygame.init()
    fenetre = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("RoboRally - Plateau")
    jeu, murs = creer_jeu()
    images = creer_images()
    ia = ControleurRobot()
    horloge = pygame.time.Clock()
    jeu.animation_callback = lambda: afficher_animation(
        fenetre, jeu, murs, images, horloge
    )
    jeu.tir_callback = lambda tireur, cible: afficher_tir(
        fenetre, jeu, murs, images, horloge, tireur, cible
    )
    en_cours = True
    temps_depuis_cycle = 0
    intervalle_ia = 250

    while en_cours:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
            elif evenement.type == pygame.KEYDOWN and evenement.key == pygame.K_ESCAPE:
                en_cours = False

        temps_depuis_cycle += horloge.get_time()
        if (
            temps_depuis_cycle >= intervalle_ia
            and jeu.equipe_gagnante is None
        ):
            jouer_un_cycle_ia(jeu, ia)
            temps_depuis_cycle = 0

        dessiner(fenetre, jeu, murs, images)
        pygame.display.flip()
        horloge.tick(60)
    pygame.quit()


def afficher_animation(fenetre, jeu, murs, images, horloge):
    """Affiche une étape de déplacement pendant une animation.

    - Description : redessine le plateau puis ralentit brièvement l'affichage.
    - Prérequis : pygame doit être initialisé et les objets de rendu valides.
    - Arguments : `fenetre` (`pygame.Surface`), `jeu` (`Jeu`), `murs` (`dict`),
      `images` (`dict`), `horloge` (`pygame.time.Clock`).
    - Retourne : rien (`None`).
    """
    dessiner(fenetre, jeu, murs, images)
    pygame.display.flip()
    horloge.tick(12)


if __name__ == "__main__":
    main()
