from dataclasses import dataclass

from Direction import Direction


@dataclass
class Carte:
    direction: Direction
    priorite: int