from __future__ import annotations

"""
Auteur : Perles Alexis
Date de dernière modification : 10/11/2026
Contenu : Lance la partie et orchestre la boucle graphique pygame.
"""

"""Lancement de RoboRally avec les robots contrôlés par une IA."""

import argparse

try:
    import pygame
except ImportError:
    pygame = None

from entites.direction import Direction
from entites.drapeau import Drapeau
from entites.robot import Robot
from regles.jeu import Jeu
from affichage.dessin import (
    TAILLE_PLATEAU,
    afficher_tir,
    dessiner,
    creer_images,
)
from regles.generation import creer_plateau
from ia import ControleurRobot
from ia.entrainement import EntraineurPerceptron
from ia.perceptron import Perceptron, charger_perceptron, erreur_quadratique_moyenne
from ia.reseau_neurones import ReseauNeurones


def creer_jeu(graine=None):
    """
    Role : assemble tous les objets nécessaires au lancement du jeu.
    Entrees : aucun.
    Sorties : partie et murs du plateau (`tuple[Jeu, dict]`).
    Pré-requis : les constantes et classes importées doivent être disponibles.
    """
    cases, murs = creer_plateau()
    robots = [
        Robot("Robot Bleu 1", 0, 0, Direction.EST, "bleu"),
        Robot("Robot Bleu 2", 1, 0, Direction.EST, "bleu"),
        Robot("Robot Rouge 1", 10, 11, Direction.OUEST, "rouge"),
        Robot("Robot Rouge 2", 11, 11, Direction.OUEST, "rouge"),
    ]
    jeu = Jeu(robots, TAILLE_PLATEAU, TAILLE_PLATEAU, cases, graine)
    jeu.drapeaux = [
        (Drapeau("bleu"), 3, 1),
        (Drapeau("bleu"), 4, 4),
        (Drapeau("rouge"), 8, 10),
        (Drapeau("rouge"), 10, 9),
    ]
    return jeu, murs


def creer_partie_evaluation():
    """
    Role : construit une partie d'évaluation avec une graine dédiée.
    Entrees : aucune
    Sorties : tuple : jeu et murs
    Pré-requis : le plateau est disponible
    """
    creer_partie_evaluation.compteur += 1
    return creer_jeu(1_000_000 + creer_partie_evaluation.compteur)


creer_partie_evaluation.compteur = 0


def jouer_un_cycle_ia(jeu, ia):
    """
    Role : prépare un tour si nécessaire, entraîne l'IA puis joue la carte courante.
    Entrees : `jeu` (`Jeu`), `ia` (`ControleurRobot`).
    Sorties : rien (`None`).
    Pré-requis : `jeu` doit être un objet `Jeu` et `ia` un objet `ControleurRobot`.
    """
    if not jeu.cartes_du_tour:
        ia.preparer_tour(jeu)
    actuelle = jeu.carte_actuelle()
    if actuelle is None:
        return
    robot, carte = actuelle
    jouer = ia.doit_jouer_carte(jeu, robot, carte)
    jeu.jouer_carte_actuelle(jouer)


def main(chemin_modele="modeles/modele_perceptron.json") -> None:
    """
    Role : initialise pygame, affiche le plateau et fait jouer l'IA.
    Entrees : chemin_modele (`str`) : fichier JSON du modèle à visualiser.
    Sorties : rien (`None`).
    Pré-requis : pygame doit être installé et les images du projet accessibles.
    """
    pygame.init()
    fenetre = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("RoboRally - Plateau")
    jeu, murs = creer_jeu()
    images = creer_images()
    ia = ControleurRobot(charger_perceptron(chemin_modele))
    jeu.controleur = ia
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
    """
    Role : redessine le plateau puis ralentit brièvement l'affichage.
    Entrees : `fenetre` (`pygame.Surface`), `jeu` (`Jeu`), `murs` (`dict`), `images` (`dict`), `horloge` (`pygame.time.Clock`).
    Sorties : rien (`None`).
    Pré-requis : pygame doit être initialisé et les objets de rendu valides.
    """
    dessiner(fenetre, jeu, murs, images)
    pygame.display.flip()
    horloge.tick(12)


def lancer_entrainement(
    nombre_parties, chemin_modele, nombre_max_tours=1000,
    nombre_parties_evaluation=400, utiliser_reseau=False,
):
    """
    Role : charge un modèle existant s'il est présent, joue plusieurs parties sans pygame et sauvegarde les nouveaux paramètres.
    Entrees : `nombre_parties` (`int`), `chemin_modele` (`str`), `nombre_max_tours` (`int`), `utiliser_reseau` (`bool`).
    Sorties : statistiques des parties (`list[dict]`).
    Pré-requis : `nombre_parties` et `nombre_max_tours` doivent être positifs.
    """
    try:
        perceptron = charger_perceptron(chemin_modele)
        if utiliser_reseau and not isinstance(perceptron, ReseauNeurones):
            raise ValueError("Le fichier contient un perceptron.")
        controleur = ControleurRobot(perceptron)
    except (FileNotFoundError, ValueError, KeyError):
        controleur = ControleurRobot(reseau=utiliser_reseau)
    entraineur = EntraineurPerceptron(
        creer_jeu,
        controleur,
        nombre_max_tours,
        creer_jeu_evaluation=creer_partie_evaluation,
    )
    resultats = entraineur.entrainer_et_sauvegarder(
        nombre_parties, chemin_modele, nombre_parties_evaluation
    )
    print(f"{nombre_parties} partie(s) d'entraînement terminée(s).")
    print(f"Modèle sauvegardé dans : {chemin_modele}")
    moyenne = sum(resultat["recompense"] for resultat in resultats) / len(resultats)
    parties_terminees = sum(
        resultat["equipe_gagnante"] is not None for resultat in resultats
    )
    print(
        "Erreur quadratique moyenne : "
        f"{erreur_quadratique_moyenne(controleur.perceptron):.4f}"
    )
    print(
        "Taux de parties terminées : "
        f"{parties_terminees / len(resultats):.2%}"
    )
    print(f"Récompense moyenne : {moyenne:.2f}")
    statistiques = controleur.perceptron.statistiques
    print(
        f"Évaluation ({nombre_parties_evaluation} parties) : "
        f"{statistiques.get('evaluation_taux_termination', 0):.2%} de parties terminées, "
        f"{statistiques.get('evaluation_accord_oracle', 0):.2%} d'accord oracle"
    )
    return resultats


def analyser_arguments():
    """
    Role : permet de choisir entre le jeu graphique et l'entraînement.
    Entrees : aucun.
    Sorties : arguments analysés (`argparse.Namespace`).
    Pré-requis : aucun.
    """
    analyseur = argparse.ArgumentParser(description="RoboRally")
    analyseur.add_argument(
        "--entrainer",
        type=int,
        metavar="PARTIES",
        help="entraîne l'IA sur le nombre de parties indiqué",
    )
    analyseur.add_argument(
        "--modele",
        default="modeles/modele_perceptron.json",
        help="fichier JSON utilisé pour charger et sauvegarder les poids",
    )
    analyseur.add_argument(
        "--tours-max",
        type=int,
        default=1000,
        help="nombre maximal de cartes jouées par partie",
    )
    analyseur.add_argument(
        "--evaluation",
        type=int,
        default=400,
        metavar="PARTIES",
        help="nombre de parties d'évaluation (minimum 400)",
    )
    analyseur.add_argument(
        "--reseau",
        action="store_true",
        help="utilise le réseau de neurones au lieu du perceptron",
    )
    return analyseur.parse_args()


if __name__ == "__main__":
    arguments = analyser_arguments()
    if arguments.entrainer is not None:
        lancer_entrainement(
            arguments.entrainer,
            arguments.modele,
            arguments.tours_max,
            arguments.evaluation,
            arguments.reseau,
        )
    else:
        main(arguments.modele)
