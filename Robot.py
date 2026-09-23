from Direction import Direction


class Robot:
    def __init__(self, nom: str, x: int, y: int, direction: Direction, couleur: str):
        self.nom = nom
        self.x = x
        self.y = y
        self.direction = direction
        self.couleur = couleur
        self.points_degat = 0
        self.vies = 3
        self.est_detruit = False