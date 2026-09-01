import json
from collections import deque
from typing import Any


class Orchestrator:
    def __init__(self, map_path: str = "data/map.json",
                 network_path: str = "data/network.json") -> None:
        try:
            with open(map_path, 'r', encoding='utf-8') as f:
                self.map_config = json.load(f)
            with open(network_path, 'r', encoding='utf-8') as f:
                self.network = json.load(f)
        except OSError as e:
            raise RuntimeError(f"Reading file error - {e}") from e

    def get_shortest_valid_path(self,
                                start_node: str,
                                goal_node: str,
                                restricted_nodes: set[str]) -> list[str]:
        if start_node in restricted_nodes or goal_node in restricted_nodes:
            return []

        queue = deque([[start_node]])
        visited = {start_node}

        while queue:
            curr_path = queue.popleft()
            curr_node = curr_path[-1]

            if curr_node == goal_node:
                return curr_path

            neighbours = self.network.get(curr_node, [])
            neighbours.sort(key=lambda n: 0 if
                            self.get_zone_type(n) == "priority" else 1)

            for neighbour in neighbours:
                if neighbour not in visited and neighbour not in restricted_nodes:
                    visited.add(neighbour)
                    queue.append(curr_path + [neighbour])
        return []

    def get_nb_drones(self) -> Any:
        return self.get_node_capacity("start")

    def get_node_capacity(self, node_name: str) -> Any:
        hub_data = self.map_config.get("Hub", {}).get(node_name, {})
        return hub_data.get("max_drones", 1)

    def get_link_capacity(self, node_a: str, node_b: str) -> Any:
        connections = self.map_config.get("Connections", {})

        link_str_1 = f"{node_a}-{node_b}"
        link_str_2 = f"{node_b}-{node_a}"

        link_data = connections.get(link_str_1) or connections.get(link_str_2, {})
        return link_data.get("max_link_capacity", 1)

    def get_zone_type(self, node_name: str) -> Any:
        return self.map_config.get("Hub", {}).get(node_name, {}).get("zone", "normal")

    def get_node_coor(self, node_name: str) -> Any:
        hub_data = self.map_config.get("Hub", {}).get(node_name, {})
        return hub_data.get("coor", [0, 0])
