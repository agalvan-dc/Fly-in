import json
from enum import Enum
from organisms import Drone
from .orquestrator import Orquestrator

class Move(Enum):
    STILL = 0
    CONNEC = 1
    MOVE = 2

class StateMachine:
    def __init__(self, orquestrator: Orquestrator) -> None:
        self.orq = orquestrator
        self.total_drones = self.orq.get_nb_drones()
        self.drones = [Drone(id=i, start_node="start") for i in range(self.total_drones)]
        self.tick = 0

    def run(self) -> None:
        while not all(d.has_arrived for d in self.drones):
            self.tick += 1
            self.simulate_tick()
            
        self.export_history("data/log.json")

    def simulate_tick(self) -> None:
        curr_node_usage = {node: 0 for node in self.orq.network}
        curr_link_usage = {}
        tick_status = {d.id: Move.STILL.value for d in self.drones}

        for d in self.drones:
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
                d.path = self.orq.get_shortest_valid_path(d.curr_node, "goal", set())
                
            target = d.next_node
            if not target: 
                continue

            link = (d.curr_node, target)
            node_cap = self.orq.get_node_capacity(target)
            link_cap = self.orq.get_link_capacity(d.curr_node, target)

            if curr_node_usage.get(target, 0) < node_cap and curr_link_usage.get(link, 0) < link_cap:
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
                d.path = self.orq.get_shortest_valid_path(d.curr_node, "goal", {target})
                tick_status[d.id] = Move.STILL.value

        for d in self.drones:
            node_for_coor = d.next_node if tick_status[d.id] == Move.CONNEC.value else d.curr_node
            
            d.history.append({
                "coor": self.orq.get_node_coor(node_for_coor),
                "status": tick_status[d.id]
            })

    def export_history(self, filepath: str) -> None:
        output = {f"drone_{d.id}": d.history for d in self.drones}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=4)
