from Direction import Direction


class Robot:
    def __init__(self, nom: str, x: int, y: int, direction: Direction, couleur: str):
        self.nom = nom
        self.x = x
        self.y = y
        self.direction = direction
        self.couleur = couleur
        self.points_degat = 1
        self.pv = 3
        self.est_detruit = False

    def deplacer(self, direction: Direction):

        if direction == Direction.NORD:
            self.y -= 1
        elif direction == Direction.EST:
            self.x += 1
        elif direction == Direction.SUD:
            self.y += 1
        elif direction == Direction.OUEST:
            self.x -= 1

    def recoit_degats(self,degats: int):
        if self.pv <= degats :
            self.est_detruit = True
        else:
            self.pv -= degats

