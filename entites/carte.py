"""
Auteur : Perles Alexis, Maelys Rameau
Date de dernière modification : 10/11/2026
Contenu : Définit les cartes de déplacement et leur génération.
"""

from dataclasses import dataclass

from entites.direction import ActionCarte


@dataclass
class Carte:
    action: ActionCarte
    vitesse: int


def carte_aleatoire(source_aleatoire):
    """
    Role : cree une carte aleatoire.
    Entrees : source_aleatoire (object) : source de hasard
    Sorties : Carte : carte creee
    Pré-requis : la source fournit choice et randint
    """
    actions = (
        ActionCarte.AVANCER,
        ActionCarte.TOURNER_DROITE,
        ActionCarte.TOURNER_GAUCHE,
    )
    return Carte(source_aleatoire.choice(actions), source_aleatoire.randint(1, 100))


def tirer_main(source_aleatoire, nombre):
    """
    Role : tire une main contenant les actions principales.
    Entrees : source_aleatoire (object) : source de hasard ; nombre (int) : nombre de cartes
    Sorties : list : cartes tirees
    Pré-requis : nombre est positif ou nul
    """
    actions = [
        ActionCarte.AVANCER,
        ActionCarte.TOURNER_DROITE,
        ActionCarte.TOURNER_GAUCHE,
    ]
    cartes = [Carte(action, source_aleatoire.randint(1, 100)) for action in actions[:nombre]]
    while len(cartes) < nombre:
        cartes.append(carte_aleatoire(source_aleatoire))
    source_aleatoire.shuffle(cartes)
    return cartes
