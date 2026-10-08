"""
Auteur : Perles Alexis
Date de dernière modification : 04/10/2026
Contenu : Définit le modèle mathématique du perceptron et son apprentissage.
"""

import json


class Perceptron:
    """Calcule un score linéaire et ajuste ses paramètres."""

    def __init__(self, poids, biais=0.0, taux_apprentissage=0.01):
        """Construit un perceptron avec ses paramètres d'apprentissage.

        - Description : initialise les poids, le biais et le taux d'apprentissage.
        - Prérequis : `poids` doit contenir au moins une valeur et
          `taux_apprentissage` doit être strictement positif.
        - Arguments : `poids` (`list` ou `tuple` de nombres), `biais` (`float`),
          `taux_apprentissage` (`float`).
        - Retourne : rien (`None`).
        """
        if not poids:
            raise ValueError("Le perceptron doit avoir au moins un poids.")
        if taux_apprentissage <= 0:
            raise ValueError("Le taux d'apprentissage doit être positif.")
        self.poids = [float(poids_element) for poids_element in poids]
        self.biais = float(biais)
        self.taux_apprentissage = float(taux_apprentissage)

    def calculer(self, caracteristiques):
        """Calcule la sortie linéaire du perceptron.

        - Description : additionne chaque caractéristique multipliée par son
          poids, puis ajoute le biais.
        - Prérequis : le nombre de caractéristiques doit correspondre au
          nombre de poids.
        - Arguments : `caracteristiques` (`list` ou `tuple` de nombres).
        - Retourne : score calculé (`float`).
        """
        if len(caracteristiques) != len(self.poids):
            raise ValueError("Le nombre de caractéristiques doit correspondre aux poids.")
        return sum(
            poids * caracteristique
            for poids, caracteristique in zip(self.poids, caracteristiques)
        ) + self.biais

    def mettre_a_jour(self, caracteristiques, cible):
        """Met à jour les paramètres du perceptron selon son erreur.

        - Description : calcule l'écart entre la cible et la prédiction, puis
          corrige les poids et le biais avec le taux d'apprentissage.
        - Prérequis : le nombre de caractéristiques doit correspondre au
          nombre de poids.
        - Arguments : `caracteristiques` (`list` ou `tuple` de nombres),
          `cible` (`float`).
        - Retourne : erreur avant correction (`float`).
        """
        erreur = float(cible) - self.calculer(caracteristiques)
        self.poids = [
            poids + self.taux_apprentissage * erreur * caracteristique
            for poids, caracteristique in zip(self.poids, caracteristiques)
        ]
        self.biais += self.taux_apprentissage * erreur
        return erreur

    def sauvegarder(self, chemin):
        """Enregistre les paramètres du perceptron dans un fichier JSON.

        - Description : conserve les poids, le biais et le taux d'apprentissage
          afin de reprendre l'entraînement lors d'une prochaine exécution.
        - Prérequis : `chemin` doit désigner un fichier accessible en écriture.
        - Arguments : `chemin` (`str` ou `Path`).
        - Retourne : rien (`None`).
        """
        with open(chemin, "w", encoding="utf-8") as fichier:
            json.dump(
                {
                    "poids": self.poids,
                    "biais": self.biais,
                    "taux_apprentissage": self.taux_apprentissage,
                },
                fichier,
                indent=2,
            )

    @classmethod
    def charger(cls, chemin):
        """Reconstruit un perceptron depuis un fichier JSON.

        - Description : lit les paramètres sauvegardés sans réinitialiser le
          modèle avec les poids par défaut.
        - Prérequis : le fichier doit contenir les trois paramètres du modèle.
        - Arguments : `chemin` (`str` ou `Path`).
        - Retourne : perceptron chargé (`Perceptron`).
        """
        with open(chemin, "r", encoding="utf-8") as fichier:
            donnees = json.load(fichier)
        return cls(
            donnees["poids"],
            donnees["biais"],
            donnees["taux_apprentissage"],
        )
