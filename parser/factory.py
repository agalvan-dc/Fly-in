import json
import sys
from typing import Any
from collections import deque

from .processor import ConnectionProcessor, HubProcessor, Processor


class Factory:
    """Parse text configuration files and initialize hub and connection objects."""

    def __init__(self, filepath: str | None = None) -> None:
        """
        Initialize the parser factory.

        Args:
            filepath: Path to the raw text map file to process.
        """
        self.nbr_drones: int = 0
        self.seen_hubs: set[str] = set()
        self.seen_connections: set[str] = set()
        self.process_file(filepath)

    def process_file(self, file_path: str | None = None) -> None:
        """
        Read and process lines from a map text file into domain objects.

        Args:
            file_path: Target file path to parse.

        Raises:
            SyntaxError: If file structure or line syntax is invalid.
            ValueError: If numerical parameters are invalid, path is missing, or duplicates are found.
        """
        path = file_path or (sys.argv[1] if len(sys.argv) > 1 else None)
        if not path:
            raise ValueError("Not enough args. Use: <program> <map.txt>")

        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        nb_drones_parsed = False

        for line_num, line in enumerate(lines, 1):
            # Remove inline comments
            clean_line = line.split('#')[0].strip()

            if not clean_line:
                continue

            if not nb_drones_parsed:
                if not clean_line.startswith("nb_drones:"):
                    raise SyntaxError(f"Line {line_num}: First functional line must be: 'nb_drones:'")
                
                parts = clean_line.split(":")
                if len(parts) != 2 or not parts[1].strip().isdigit():
                    raise SyntaxError(f"Line {line_num}: Incorrect Format 'nb_drones: <int>'")

                self.nbr_drones = int(parts[1].strip())
                if self.nbr_drones <= 0:
                    raise ValueError(f"Line {line_num}: 'nb_drones' must be > 0")

                nb_drones_parsed = True
                continue

            if ":" not in clean_line:
                raise SyntaxError(f"Line {line_num}: Line not recognised '{clean_line}'")

            tag, content = [p.strip() for p in clean_line.split(":", 1)]
            restrictions: dict[str, Any] = {}
            base_content = content

            if "[" in content:
                parts = content.split("[")
                if len(parts) > 2:
                    raise SyntaxError(f"Line {line_num}: Multiple bracket pairs found")
                
                base_content = parts[0].strip()
                rest = parts[1].strip()
                
                if not rest.endswith("]"):
                    raise SyntaxError(f"Line {line_num}: Unclosed bracket or extra trailing characters")
                
                metadata_str = rest[:-1].strip()
                if metadata_str:
                    for pair in metadata_str.split():
                        if "=" not in pair:
                            raise SyntaxError(f"Line {line_num}: Bad metadata format: '{pair}'")
                        key, value = pair.split("=", 1)
                        restrictions[key] = int(value) if value.isdigit() else value

            base_tokens = base_content.split()

            if tag in ("start_hub", "hub", "end_hub"):
                if len(base_tokens) != 3:
                    raise SyntaxError(f"Line {line_num}: Hub format must be '<name> <x> <y>'")
                
                name, x_str, y_str = base_tokens
                
                # Validate duplicate hubs
                if name in self.seen_hubs:
                    raise ValueError(f"Line {line_num}: Duplicate hub detected '{name}'")
                self.seen_hubs.add(name)

                allowed_hub_keys = {"color", "max_drones", "zone", "is_start", "is_end"}
                for k in restrictions:
                    if k not in allowed_hub_keys:
                        raise SyntaxError(f"Line {line_num}: Unrecognised hub key '{k}'")

                if not (x_str.lstrip('-').isdigit() and y_str.lstrip('-').isdigit()):
                    raise ValueError(f"Line {line_num}: Coordinates must be integers")
                
                coor = (int(x_str), int(y_str))

                if tag == "start_hub":
                    restrictions["is_start"] = True
                elif tag == "end_hub":
                    restrictions["is_end"] = True

                if tag in ("start_hub", "end_hub") and "max_drones" not in restrictions:
                    restrictions["max_drones"] = self.nbr_drones

                HubProcessor(name=name, coor=coor, **restrictions)

            elif tag == "connection":
                if len(base_tokens) != 1:
                    raise SyntaxError(f"Line {line_num}: Invalid Connection format")
                
                conn_name = base_tokens[0]
                
                # Validate duplicate connections
                if conn_name in self.seen_connections:
                    raise ValueError(f"Line {line_num}: Duplicate connection detected '{conn_name}'")
                self.seen_connections.add(conn_name)

                allowed_conn_keys = {"max_link_capacity"}
                for k in restrictions:
                    if k not in allowed_conn_keys:
                        raise SyntaxError(f"Line {line_num}: Unrecognised connection key '{k}'")

                ConnectionProcessor(name=conn_name, **restrictions)
            else:
                raise SyntaxError(f"Line {line_num}: Forbidden tag '{tag}'")

        if not nb_drones_parsed:
            raise SyntaxError("File does not contain 'nb_drones:' as first line")
        
        Processor.format()


class Linkers:
    """Build topological network connections from processed map JSON data."""

    def __init__(self, filepath: str = "data/map.json") -> None:
        """
        Initialize Linkers and construct network topology output.

        Args:
            filepath: Path to the generated map JSON configuration file.
        """
        self.filepath = filepath
        self.connections()

    def connections(self) -> None:
        """
        Read map data, validate pathways, and output an adjacency list network file.

        Raises:
            ValueError: If connections reference nonexistent hubs, or if no valid path exists to the end hub.
        """
        net: dict[str, list[str]] = {}

        with open(self.filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        hubs = data.get('Hub', {})
        connections = data.get('Connections', {})
        
        start_nodes = []
        end_nodes = []
        
        # Identify start and end nodes
        for h_name, h_data in hubs.items():
            if h_data.get('is_start'):
                start_nodes.append(h_name)
            if h_data.get('is_end'):
                end_nodes.append(h_name)

        for name in hubs:
            linked_hubs = set()

            for conec in connections.keys():
                split_conec = conec.split('-')
                
                # Ensure connection nodes exist in the map
                if split_conec[0] not in hubs or split_conec[1] not in hubs:
                    raise ValueError(f"Invalid connection: '{conec}' references a non-existent hub.")

                if name in split_conec:
                    neighbor = split_conec[0] if split_conec[0] != name else split_conec[1]
                    linked_hubs.add(neighbor)

            net[name] = list(linked_hubs)
            
        # Check if goal is reachable using BFS
        if start_nodes and end_nodes:
            reachable = False
            for start in start_nodes:
                visited = set()
                queue = deque([start])
                while queue:
                    curr = queue.popleft()
                    if curr in end_nodes:
                        reachable = True
                        break
                    if curr not in visited:
                        visited.add(curr)
                        queue.extend(net.get(curr, []))
                if reachable:
                    break
            
            if not reachable:
                raise ValueError("Validation failed: No valid path exists to reach the end_hub.")
        else:
            raise ValueError("Incomplete configuration: Missing at least one start_hub or end_hub.")

        output_path = "data/network.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(net, f, indent=4)
        print(f"Network generated in: {output_path}")
