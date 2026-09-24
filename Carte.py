from dataclasses import dataclass

from Direction import Direction


@dataclass
class Carte:
    direction: Direction
    vitesse: int

    @staticmethod
    def aleatoire(aleatoire):
        return Carte(
            aleatoire.choice(list(Direction)),
            aleatoire.randint(1, 100),
        )

    @staticmethod
    def main_aleatoire(aleatoire, nombre):
        return [Carte.aleatoire(aleatoire) for _ in range(nombre)]