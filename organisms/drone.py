from typing import Any

class Drone:
    def __init__(self, start_node: str, drone_id: int) -> None:
        self.drone_id: int = drone_id
        self.curr_node: str = start_node
        self.path: list[str] = []
        self.path_index: int = 0
        self.transit_turns: int = 0
        self.history: dict[str, Any] = {}

    @property
    def has_arrived(self) -> bool:
        return bool(self.path) and self.curr_node == self.path[-1]

    @property
    def next_node(self) -> str | None:
        if self.path_index + 1 < len(self.path):
            return self.path[self.path_index + 1]
        return None

    def advance(self) -> None:
        if self.next_node:
            self.path_index += 1
            self.curr_node = self.path[self.path_index]

