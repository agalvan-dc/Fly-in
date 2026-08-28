from organisms import Drone
from enum import Enum
from collections import deque

import json

class mov(Enum):
    STILL = 0
    CONNEC_MOVE = 1
    MOVE = 2


class Orchestrator:
    def __init__(self, map_path: str = "data/map.json",
                 network_path: str = "data/network.json") -> None:
        self.paths: list[list[str]] = []

        try:
            with open(map_path, 'r', encoding='utf-8') as f:
                self.map = json.load(f)
            with open(network_path, 'r', encoding='utf-8') as f:
                self.network = json.load(f)
        except OSError as e:
            raise RuntimeError(f"Reading file error - {e}") from e

    def bfs(self, max_depth: int = 45) -> None:
        all_nodes = set(self.network) | {n for neigh in self.network.values() for n in neigh}
        if "start" not in all_nodes or "goal" not in all_nodes:
            raise ValueError("No start or goal node found. Aborting...")

        queue = deque([["start"]])
        self.paths = []

        while queue:
            curr_path = queue.popleft()
            curr_node = curr_path[-1]

            if len(curr_path) > max_depth:
                continue
            if curr_node == "goal":
                self.paths.append(curr_path)
                continue

            for neighbour in self.network.get(curr_node, []):
                if neighbour not in curr_path:
                    queue.append(curr_path + [neighbour])

        self.paths.sort(key=len)
