class Drone:
    """Represent an individual drone entity navigating through the graph network."""

    def __init__(self, start_node: str, id: int) -> None:
        """
        Initialize a Drone instance.

        Args:
            start_node: The starting node identifier where the drone spawns.
            id: The unique identifier for the drone.
        """
        self.id: int = id
        self.curr_node: str = start_node
        self.path: list[str] = []
        self.path_index: int = 0
        self.transit_turns: int = 0

    @property
    def has_arrived(self) -> bool:
        """
        Check if the drone has reached its final destination.

        Returns:
            True if the drone has a path and is at the final node, False otherwise.
        """
        return bool(self.path) and self.curr_node == self.path[-1]

    @property
    def next_node(self) -> str | None:
        """
        Retrieve the next node identifier in the drone's assigned path.

        Returns:
            The identifier of the next node, or None if at the end of the path.
        """
        if self.path_index + 1 < len(self.path):
            return self.path[self.path_index + 1]
        return None

    def advance(self) -> None:
        """Advance the drone to the next node along its assigned path."""
        if self.next_node:
            self.path_index += 1
            self.curr_node = self.path[self.path_index]
