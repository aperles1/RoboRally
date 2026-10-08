"""
Auteur : Perles Alexis
Date de dernière modification : 30/09/2026
Contenu : Modélise les robots, leurs déplacements et leurs états.
"""

from Entitées.Direction import Direction


class Robot:
    """Robot jouable, rattaché à une équipe par sa couleur."""

    def __init__(self, nom: str, x: int, y: int, orientation: Direction, couleur: str):
        """Construit un robot avec sa position et son état initial.

        - Description : initialise l'identité, l'équipe, les points de vie et les bonus.
        - Prérequis : `orientation` doit être un membre de `Direction`.
        - Arguments : `nom` (`str`), `x` (`int`), `y` (`int`),
          `orientation` (`Direction`), `couleur` (`str`).
        - Retourne : rien (`None`).
        """
        self.nom = nom
        self.x = x
        self.y = y
        self.orientation = orientation
        self.couleur = couleur
        self.pv = 3
        self.est_detruit = False
        self.bonus_degats = 0
        self.bouclier = 0
        self.positions_precedentes = []

    def deplacer(self, direction: Direction) -> None:
        """Déplace le robot d'une case dans une direction.

        - Description : ajoute le vecteur de direction aux coordonnées du robot.
        - Prérequis : `direction` doit être un membre de `Direction`.
        - Arguments : `direction` (`Direction`).
        - Retourne : rien (`None`).
        """
        dx, dy = direction.value
        self.x += dx
        self.y += dy

    def recoit_degats(self, degats=1):
        """Applique des dégâts au robot et peut le détruire.

        - Description : consomme d'abord un bouclier, sinon retire des points de vie.
        - Prérequis : `degats` doit être un entier positif ou nul.
        - Arguments : `degats` (`int`, valeur par défaut : `1`).
        - Retourne : rien (`None`).
        """
        if self.bouclier > 0:
            self.bouclier -= 1
            return
        self.pv = max(0, self.pv - degats)
        self.est_detruit = self.pv == 0

    def utiliser_case_bonus(self, type_bonus, aleatoire):
        """Applique l'effet d'une case de réparation ou de bonus.

        - Description : restaure un point de vie ou attribue une amélioration aléatoire.
        - Prérequis : `type_bonus` vaut `reparation` ou `bonus`; `aleatoire`
          fournit `choice`.
        - Arguments : `type_bonus` (`str`), `aleatoire` (`random.Random` ou
          objet compatible).
        - Retourne : rien (`None`).
        """
        if type_bonus == "reparation":
            self.pv = min(3, self.pv + 1)
        elif type_bonus == "bonus":
            if aleatoire.choice(["degats", "bouclier"]) == "degats":
                self.bonus_degats = 2
            else:
                self.bouclier = 2
