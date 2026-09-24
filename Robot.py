from Direction import Direction


class Robot:
    """Robot jouable, rattaché à une équipe par sa couleur."""

    def __init__(self, nom: str, x: int, y: int, direction: Direction, couleur: str):
        self.nom = nom
        self.x = x
        self.y = y
        self.direction = direction
        self.couleur = couleur
        self.pv = 3
        self.est_detruit = False
        self.bonus_degats = 0
        self.bouclier = 0

    def deplacer(self, direction: Direction) -> None:
        dx, dy = direction.value
        self.x += dx
        self.y += dy

    def recoit_degats(self, degats=1):
        if self.bouclier > 0:
            self.bouclier -= 1
            return
        self.pv = max(0, self.pv - degats)
        self.est_detruit = self.pv == 0

    def utiliser_case_bonus(self, type_bonus, aleatoire):
        if type_bonus == "reparation":
            self.pv = min(3, self.pv + 1)
        elif type_bonus == "bonus":
            if aleatoire.choice(["degats", "bouclier"]) == "degats":
                self.bonus_degats = 2
            else:
                self.bouclier = 2
