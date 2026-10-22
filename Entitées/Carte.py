"""
Auteur : Perles Alexis, Maelys Rameau
Date de dernière modification : 22/10/2026
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
        """Crée une carte avec une action autorisée et une vitesse aléatoires.

        Le recul reste reconnu pour lire d'anciennes cartes, mais n'est plus
        distribué dans les nouvelles mains.
        - Prérequis : `aleatoire` doit fournir `choice` et `randint`.
        - Arguments : `aleatoire` (`random.Random` ou objet compatible).
        - Retourne : carte générée (`Carte`).
        """
        actions_autorisees = (
            ActionCarte.AVANCER,
            ActionCarte.TOURNER_DROITE,
            ActionCarte.TOURNER_GAUCHE,
        )
        action_choisie = source_aleatoire.choice(actions_autorisees)
        vitesse_choisie = source_aleatoire.randint(1, 100)
        return Carte(action=action_choisie, vitesse=vitesse_choisie)