"""
Auteur : Perles Alexis
Date de dernière modification : 30/09/2026
Contenu : Définit les cartes de déplacement et leur génération aléatoire.
"""

from dataclasses import dataclass

from Entitées.Direction import Direction


@dataclass
class Carte:
    direction: Direction
    vitesse: int

    @staticmethod
    def aleatoire(aleatoire):
        """Crée une carte avec une direction et une vitesse aléatoires.

        - Description : tire une direction puis une priorité entre 1 et 100.
        - Prérequis : `aleatoire` doit fournir `choice` et `randint`.
        - Arguments : `aleatoire` (`random.Random` ou objet compatible).
        - Retourne : carte générée (`Carte`).
        """
        return Carte(
            aleatoire.choice(list(Direction)),
            aleatoire.randint(1, 100),
        )