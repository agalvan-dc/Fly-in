import json
from enum import Enum
from typing import Any

from organisms import Drone

from .orquestrator import Orchestrator


class Move(Enum):
    """Represent the possible movement states of a drone during a simulation tick."""

    STILL = 0
    CONNEC = 1
    MOVE = 2


class StateMachine:
    """Manage and execute the step-by-step simulation state for all active drones."""

    def __init__(self, orquestrator: Orchestrator) -> None:
        """
        Initialize the state machine using the orchestrator context.

        Args:
            orquestrator: The orchestrator containing map and network data.
        """
        self.orq = orquestrator
        self.start_node = self._resolve_node(is_start=True)
        self.goal_node = self._resolve_node(is_start=False)
        self.total_drones = self.orq.get_node_capacity(self.start_node)
        self.drones = [
            Drone(id=i, start_node=self.start_node)
            for i in range(self.total_drones)
        ]
        self.tick = 0
        self.log: dict[int, Any] = {}
        self.txt_log: list[str] = []
        self.congestion: dict[str, float] = {}
        self.run()

    def _resolve_node(self, is_start: bool) -> Any:
        """
        Dynamically determine the start or goal node identifier from map metadata.

        Args:
            is_start: True to look for the start node, False for the goal node.

        Returns:
            The identifier of the resolved node.
        """
        hubs = self.orq.map_config.get("Hub", {})
        flag = "is_start" if is_start else "is_end"
        default_names = (
            ("start", "start_node", "start_hub")
            if is_start
            else ("goal", "end", "end_node", "end_hub")
        )

        for name, data in hubs.items():
            if data.get(flag) or name.lower() in default_names:
                return name

        hub_keys = list(hubs.keys())
        if hub_keys:
            return hub_keys[0] if is_start else hub_keys[-1]
        return "start" if is_start else "goal"

    def _register_block(self, node: str) -> None:
        self.congestion[node] = self.congestion.get(node, 0) + 1

    def _decay_congestion(self) -> None:
        for node in list(self.congestion):
            self.congestion[node] *= 0.9
            if self.congestion[node] < 0.05:
                del self.congestion[node]

    def _plan_path(self, curr_node: str,
                   forced_avoid: set[str] | None = None) -> list[str]:
        forced_avoid = forced_avoid or set()
        path = self.orq.get_shortest_valid_path(curr_node, "goal", forced_avoid)
        if not path:
            return path
        hotspots = {n for n in path
                    if self.congestion.get(n, 0)
                    >= self.orq.get_node_capacity(n)} - forced_avoid

        if not hotspots:
            return path
        detour = self.orq.get_shortest_valid_path(curr_node,
                                                  "goal",
                                                  forced_avoid | hotspots)
        if detour and len(detour) <= len(path) + 2:
            return detour
        return path

    def run(self) -> None:
        """Execute the main simulation loop until all drones reach their target node."""
        while not all(d.has_arrived for d in self.drones):
            self.tick += 1
            self.simulate_tick()

        print(f"\033[32;1m  Sim ended in {self.tick} turns\033[0m")
        self.export_history("data/log.json", "data/movements.txt")

    def simulate_tick(self) -> None:
        """Simulate a single time step (tick) for all active drones."""
        curr_node_usage = {node: 0 for node in self.orq.network}
        curr_link_usage: dict[Any, Any] = {}
        tick_status = {d.id: Move.STILL.value for d in self.drones}
        self._decay_congestion()

        for d in self.drones:
            if d.has_arrived:
                continue
            if d.transit_turns > 0:
                link = (d.curr_node, d.next_node)
                curr_link_usage[link] = curr_link_usage.get(link, 0) + 1
            else:
                curr_node_usage[d.curr_node] += 1

        for d in self.drones:
            if d.has_arrived:
                tick_status[d.id] = Move.STILL.value
                continue

            if d.transit_turns > 0:
                d.transit_turns -= 1
                if d.transit_turns == 0:
                    d.advance()
                    tick_status[d.id] = Move.MOVE.value
                else:
                    tick_status[d.id] = Move.CONNEC.value
                continue

            if not d.path:
                d.path = self._plan_path(d.curr_node)
                d.path_index = 0

            target = d.next_node
            if not target:
                tick_status[d.id] = Move.STILL.value
                continue

            link = (d.curr_node, target)
            node_cap = self.orq.get_node_capacity(target)
            link_cap = self.orq.get_link_capacity(d.curr_node, target)

            if (curr_node_usage.get(target, 0) < node_cap
               and curr_link_usage.get(link, 0) < link_cap):
                curr_node_usage[d.curr_node] -= 1
                curr_link_usage[link] = curr_link_usage.get(link, 0) + 1

                if self.orq.get_zone_type(target) == "restricted":
                    d.transit_turns = 1
                    tick_status[d.id] = Move.CONNEC.value
                else:
                    d.advance()
                    curr_node_usage[target] += 1
                    tick_status[d.id] = Move.MOVE.value

            else:
                self._register_block(target)
                new_path = self._plan_path(d.curr_node, forced_avoid={target})
                if new_path:
                    curr_path_cost = len(d.path) - d.path_index
                    new_path_cost = len(new_path)

                    if new_path_cost < curr_path_cost + 1:
                        d.path = new_path
                        d.path_index = 0

                tick_status[d.id] = Move.STILL.value

        log = []
        for d in self.drones:
            log.append({
                "drone": d.id,
                "coor": self.orq.get_node_coor(d.curr_node),
                "status": tick_status[d.id]
            })
        self.log[self.tick] = log

        turn_movements = []
        for d in self.drones:
            status = tick_status[d.id]
            if status == Move.MOVE.value:
                turn_movements.append(f"D{d.id}-{d.curr_node}")
            elif status == Move.CONNEC.value:
                turn_movements.append(f"D{d.id}-{d.curr_node}-{d.next_node}")

        if turn_movements:
            self.txt_log.append(" ".join(turn_movements))

    def export_history(self, json_path: str, txt_path: str) -> None:
        """
        Export simulation log data to JSON and plain text files.

        Args:
            json_path: File path to save the structured JSON execution log.
            txt_path: File path to save the human-readable text movements.
        """
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.log, f, indent=4)

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.txt_log))
