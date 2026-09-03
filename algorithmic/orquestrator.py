import json
from collections import deque
from typing import Any


class Orchestrator:
    """Manage map configurations and route calculations for drones."""

    def __init__(self, map_path: str = "data/map.json",
                 network_path: str = "data/network.json") -> None:
        """
        Initialize the orchestrator with map and network data.

        Args:
            map_path: The file path to the map configuration JSON.
            network_path: The file path to the network topology JSON.

        Raises:
            RuntimeError: If there is an OS error reading the JSON files.
        """
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
        """
        Calculate the shortest valid path between two nodes using BFS.

        Pathfinding avoids restricted nodes and prioritizes nodes located
        in a priority zone.

        Args:
            start_node: The starting node identifier.
            goal_node: The target node identifier.
            restricted_nodes: A set of node identifiers to avoid.

        Returns:
            A list of node identifiers representing the shortest path,
            or an empty list if no valid path exists.
        """
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
        """
        Retrieve the total number of drones based on the start node capacity.

        Returns:
            The maximum number of drones the start node can hold.
        """
        return self.get_node_capacity("start")

    def get_node_capacity(self, node_name: str) -> Any:
        """
        Retrieve the maximum drone capacity for a specific node.

        Args:
            node_name: The identifier of the node.

        Returns:
            The maximum capacity of the node, defaulting to 1 if not found.
        """
        hub_data = self.map_config.get("Hub", {}).get(node_name, {})
        return hub_data.get("max_drones", 1)

    def get_link_capacity(self, node_a: str, node_b: str) -> Any:
        """
        Retrieve the maximum capacity for a connection between two nodes.

        Checks for the link definition in both directions (A-B and B-A).

        Args:
            node_a: The first node identifier.
            node_b: The second node identifier.

        Returns:
            The maximum link capacity, defaulting to 1 if not found.
        """
        connections = self.map_config.get("Connections", {})

        link_str_1 = f"{node_a}-{node_b}"
        link_str_2 = f"{node_b}-{node_a}"

        link_data = connections.get(link_str_1) or connections.get(link_str_2, {})
        return link_data.get("max_link_capacity", 1)

    def get_zone_type(self, node_name: str) -> Any:
        """
        Retrieve the zone classification of a specific node.

        Args:
            node_name: The identifier of the node.

        Returns:
            The zone type as a string, defaulting to "normal" if not found.
        """
        return self.map_config.get("Hub", {}).get(node_name, {}).get("zone", "normal")

    def get_node_coor(self, node_name: str) -> Any:
        """
        Retrieve the spatial coordinates of a specific node.

        Args:
            node_name: The identifier of the node.

        Returns:
            A list representing the [x, y] coordinates, defaulting to [0, 0].
        """
        hub_data = self.map_config.get("Hub", {}).get(node_name, {})
        return hub_data.get("coor", [0, 0])
