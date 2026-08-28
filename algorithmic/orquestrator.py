from organisms import Drone
from organisms import Node
from enum import Enum


class mov(Enum):
    STILL = 0
    CONNEC_MOVE = 1
    MOVE = 2


class Orquestrator:
    def __init__(self, filepath: str, ) -> None:

