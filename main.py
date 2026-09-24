"""Lancement du plateau RoboRally avec les robots immobiles."""

import pygame

from Drapeau import Drapeau
from Direction import Direction
from Jeu import Jeu
from Plateau import HAUTEUR, LARGEUR, TAILLE_PLATEAU, dessiner, creer_images, creer_plateau
from Robot import Robot


def creer_jeu():
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
    # La partie est volontairement en mode présentation : aucun tour ni carte
    # n'est joué tant que les règles de déplacement ne sont pas réintroduites.
    jeu.mains = {}
    jeu.cartes_du_tour = []
    return jeu, murs


def main() -> None:
    pygame.init()
    fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("RoboRally - Plateau")
    jeu, murs = creer_jeu()
    images = creer_images()
    horloge = pygame.time.Clock()
    en_cours = True

    while en_cours:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False

        dessiner(fenetre, jeu, murs, images)
        pygame.display.flip()
        horloge.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
