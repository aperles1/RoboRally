from dataclasses import dataclass

from Direction import Direction


@dataclass
class Carte:
    direction: Direction
    vitesse: int