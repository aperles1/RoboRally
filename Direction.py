from enum import Enum


class Direction(Enum):
    NORD = (0, -1)
    EST = (1, 0)
    SUD = (0, 1)
    OUEST = (-1, 0)