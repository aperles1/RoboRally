"""
Auteur : Perles Alexis
Date de dernière modification : 30/09/2026
Contenu : Définit les cartes de déplacement et leur génération aléatoire.
"""

from dataclasses import dataclass


from Entitées.Direction import ActionCarte


@dataclass
class Carte:
    action: ActionCarte
    vitesse: int

    @staticmethod
    def aleatoire(source_aleatoire):
        """Crée une carte avec une direction et une vitesse aléatoires.

        - Description : tire une direction puis une priorité entre 1 et 100.
        - Prérequis : `aleatoire` doit fournir `choice` et `randint`.
        - Arguments : `aleatoire` (`random.Random` ou objet compatible).
        - Retourne : carte générée (`Carte`).
        """

        action_choisie= source_aleatoire.choice(list(ActionCarte))
        vitesse_choisie = source_aleatoire.randint(1, 100)
        return Carte(action=action_choisie, vitesse=vitesse_choisie)