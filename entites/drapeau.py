"""
Auteur : Perles Alexis
Date de dernière modification : 10/11/2026
Contenu : Modélise les drapeaux et leur équipe de capture.
"""

from dataclasses import dataclass, field

@dataclass
class Drapeau:
    couleur: str
    couleur_origine: str = field(init=False)
    equipe_capture: str = field(init=False, default=None)

    def __post_init__(self):
        """
        Role : prépare l'état de suivi d'un drapeau après sa création.
        Entrees : aucun argument explicite (`couleur` est fourni au dataclass).
        Sorties : rien (`None`).
        Pré-requis : `couleur` doit être une chaîne représentant une équipe.
        """
        self.couleur_origine = self.couleur