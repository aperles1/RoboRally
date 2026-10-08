"""
Auteur : Perles Alexis
Date de dernière modification : 30/09/2026
Contenu : Modélise les drapeaux et leur équipe de capture.
"""

from dataclasses import dataclass, field

@dataclass
class Drapeau:
    couleur: str
    couleur_origine: str = field(init=False)
    equipe_capture: str | None = field(init=False, default=None)

    def __post_init__(self):
        """Mémorise la couleur d'origine et réinitialise la capture.

        - Description : prépare l'état de suivi d'un drapeau après sa création.
        - Prérequis : `couleur` doit être une chaîne représentant une équipe.
        - Arguments : aucun argument explicite (`couleur` est fourni au dataclass).
        - Retourne : rien (`None`).
        """
        self.couleur_origine = self.couleur