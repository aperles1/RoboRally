"""
Auteur : Perles Alexis
Date de dernière modification : 10/11/2026
Contenu : Entraîne puis sauvegarde le perceptron.
"""

import sys
from pathlib import Path

RACINE = Path(__file__).parent.parent
sys.path.insert(0, str(RACINE))

from ia.controleur import ControleurRobot
from ia.entrainement import EntraineurPerceptron
from ia.perceptron import charger_perceptron
from ia.reseau_neurones import ReseauNeurones
from main import creer_jeu


def creer_partie():
    """
    Role : construit une partie d'entraînement.
    Entrees : aucune
    Sorties : tuple : jeu et murs
    Pré-requis : le plateau est disponible
    """
    return creer_jeu()


def creer_fonction_evaluation():
    """
    Role : construit une partie d'évaluation avec une graine dédiée.
    Entrees : aucune
    Sorties : tuple : jeu et murs
    Pré-requis : le plateau est disponible
    """
    creer_fonction_evaluation.compteur += 1
    return creer_jeu(1_000_000 + creer_fonction_evaluation.compteur)


creer_fonction_evaluation.compteur = 0


def entrainer(nombre_parties, chemin_modele, utiliser_reseau=False):
    """
    Role : entraîne le modèle sur le nombre demandé de parties.
    Entrees : nombre_parties (int) : repetitions ; chemin_modele (Path) : fichier de sortie ; utiliser_reseau (bool) : choix du modèle
    Sorties : aucune
    Pré-requis : nombre_parties est positif
    """
    try:
        perceptron = charger_perceptron(chemin_modele)
        if utiliser_reseau and not isinstance(perceptron, ReseauNeurones):
            raise ValueError("Le fichier contient un perceptron.")
        controleur = ControleurRobot(perceptron)
    except (FileNotFoundError, ValueError, KeyError):
        controleur = ControleurRobot(reseau=utiliser_reseau)
    entraineur = EntraineurPerceptron(
        creer_partie,
        controleur,
        creer_jeu_evaluation=creer_fonction_evaluation,
    )
    entraineur.entrainer_et_sauvegarder(nombre_parties, chemin_modele)


if __name__ == "__main__":
    entrainer(1000, RACINE / "modeles" / "modele_perceptron.json")
