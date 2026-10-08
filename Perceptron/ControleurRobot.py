"""
Auteur : Perles Alexis
Date de dernière modification : 04/10/2026
Contenu : Contrôle les robots et sélectionne les cartes avec un perceptron.
"""

from Entitées.Carte import Carte
from Perceptron.Caracteristiques import (
    direction_possible,
    extraire_caracteristiques,
)
from Perceptron.ModelePerceptron import Perceptron


# Ces paramètres initiaux donnent un comportement raisonnable avant
# l'apprentissage et peuvent ensuite être modifiés par mettre_a_jour.
POIDS_INITIAUX = (
    1000.0, 20.0, 3.0, 10.0, 12.0, 6.0,
    -100.0, 12.0, -18.0, -18.0, -30.0, 1.0,
)


def score_perceptron(jeu, robot, direction, perceptron=None):
    """Calcule le score d'une action avec le modèle du perceptron.

    - Description : extrait les caractéristiques de l'action puis applique la
      formule linéaire du perceptron.
    - Prérequis : `direction` doit être une direction valide.
    - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `direction` (`Direction`),
      `perceptron` (`Perceptron` ou `None`).
    - Retourne : score de l'action (`float`).
    """
    modele = perceptron or Perceptron(POIDS_INITIAUX)
    caracteristiques = extraire_caracteristiques(jeu, robot, direction)
    return modele.calculer(caracteristiques)


class ControleurRobot:
    """Applique les décisions du perceptron aux cartes du jeu."""

    def __init__(self, perceptron=None):
        """Construit un contrôleur avec un perceptron.

        - Description : utilise le modèle fourni ou crée un modèle avec les
          poids initiaux du projet.
        - Prérequis : `perceptron` doit fournir `calculer` et `mettre_a_jour`.
        - Arguments : `perceptron` (`Perceptron` ou `None`).
        - Retourne : rien (`None`).
        """
        self.perceptron = perceptron or Perceptron(POIDS_INITIAUX)

    def extraire_caracteristiques(self, jeu, robot, carte):
        """Extrait les données du jeu correspondant à une carte.

        - Description : transmet la direction et la vitesse de la carte au
          module d'extraction.
        - Prérequis : `carte` doit être une instance de `Carte`.
        - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `carte` (`Carte`).
        - Retourne : caractéristiques de la carte (`list[float]`).
        """
        return extraire_caracteristiques(
            jeu, robot, carte.direction, carte.vitesse
        )

    def score_carte(self, jeu, robot, carte):
        """Calcule le score d'une carte avec la formule du perceptron.

        - Description : extrait les caractéristiques puis applique les poids
          et le biais du modèle.
        - Prérequis : `carte` doit être une instance de `Carte`.
        - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `carte` (`Carte`).
        - Retourne : score de la carte (`float`).
        """
        return self.perceptron.calculer(
            self.extraire_caracteristiques(jeu, robot, carte)
        )

    def mettre_a_jour(self, jeu, robot, carte, cible):
        """Apprend au perceptron le score attendu pour une carte.

        - Description : calcule les caractéristiques puis corrige les
          paramètres du modèle selon la cible fournie.
        - Prérequis : `cible` doit être une valeur numérique.
        - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `carte` (`Carte`),
          `cible` (`float`).
        - Retourne : erreur avant mise à jour (`float`).
        """
        caracteristiques = self.extraire_caracteristiques(jeu, robot, carte)
        return self.perceptron.mettre_a_jour(caracteristiques, cible)

    def tirer_et_choisir_cartes(self, jeu, robot):
        """Tire cinq cartes et sélectionne les trois mieux notées.

        - Description : génère les cartes puis choisit successivement celle
          dont le score du perceptron est le plus élevé.
        - Prérequis : `jeu` doit fournir un générateur aléatoire.
        - Arguments : `jeu` (`Jeu`), `robot` (`Robot`).
        - Retourne : cartes sélectionnées (`list[Carte]`).
        """
        cartes = [
            Carte.aleatoire(jeu.aleatoire)
            for _ in range(jeu.CARTES_A_TIRER)
        ]
        cartes_choisies = []
        for _ in range(jeu.CARTES_PAR_ROBOT):
            meilleure_carte = max(
                cartes, key=lambda carte: self.score_carte(jeu, robot, carte)
            )
            cartes_choisies.append(meilleure_carte)
            cartes.remove(meilleure_carte)
        return cartes_choisies

    def preparer_tour(self, jeu):
        """Fait choisir trois cartes à chaque robot actif.

        - Description : prépare les cartes de chaque robot et les installe
          dans l'ordre des manches du jeu.
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
        """Indique qu'une carte choisie doit toujours être jouée.

        La carte est consommée même si son déplacement ne peut pas être
        effectué. Le moteur conserve alors la position du robot inchangée.

        - Prérequis : `jeu`, `robot` et `carte` doivent être valides.
        - Arguments : `jeu` (`Jeu`), `robot` (`Robot`), `carte` (`Carte`).
        - Retourne : toujours `True` (`bool`).
        """
        return True
