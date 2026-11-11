"""
Auteur : Perles Alexis, Maelys Rameau
Date de dernière modification : 10/11/2026
Contenu : Modélise les robots et leurs états.
"""

from dataclasses import dataclass, field

from entites.direction import ActionCarte, Direction, tourner_droite, tourner_gauche


@dataclass(eq=False)
class Robot:
    nom: str
    x: int
    y: int
    orientation: Direction
    couleur: str
    pv: int = 3
    est_detruit: bool = False
    bonus_degats: int = 0
    bouclier: int = 0
    positions_recentes: list = field(default_factory=list)
    actions_recentes: list = field(default_factory=list)

    def __post_init__(self):
        """
        Role : initialise l'historique de position du robot.
        Entrees : aucune
        Sorties : aucune
        Pré-requis : x et y sont les coordonnees initiales
        """
        if not self.positions_recentes:
            self.positions_recentes.append((self.x, self.y))

    def deplacer(self, direction):
        """
        Role : deplace le robot d'une case.
        Entrees : direction (Direction) : direction du déplacement
        Sorties : aucune
        Pré-requis : direction est une valeur de Direction
        """
        self.x += direction.value[0]
        self.y += direction.value[1]

    def recoit_degats(self, degats=1):
        """
        Role : applique des degats au robot.
        Entrees : degats (int) : nombre de degats
        Sorties : aucune
        Pré-requis : degats est positif ou nul
        """
        if self.bouclier > 0:
            self.bouclier -= 1
            return
        self.pv = max(0, self.pv - degats)
        self.est_detruit = self.pv == 0

    def utiliser_case_bonus(self, type_bonus, aleatoire):
        """
        Role : applique l'effet d'une case de bonus.
        Entrees : type_bonus (str) : type de bonus ; aleatoire (object) : hasard
        Sorties : aucune
        Pré-requis : type_bonus vaut reparation ou bonus
        """
        if type_bonus == "reparation":
            self.pv = min(3, self.pv + 1)
        elif type_bonus == "bonus":
            if aleatoire.choice(["degats", "bouclier"]) == "degats":
                self.bonus_degats = 2
            else:
                self.bouclier = 2

    def executer_action(self, action):
        """
        Role : execute une rotation ou un deplacement.
        Entrees : action (ActionCarte) : action a effectuer
        Sorties : aucune
        Pré-requis : action est une action de carte
        """
        if action == ActionCarte.AVANCER:
            self.deplacer(self.orientation)
        elif action == ActionCarte.TOURNER_GAUCHE:
            self.orientation = tourner_gauche(self.orientation)
        elif action == ActionCarte.TOURNER_DROITE:
            self.orientation = tourner_droite(self.orientation)
