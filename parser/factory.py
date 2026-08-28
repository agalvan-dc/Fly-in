import re
import sys
import json
from typing import Any
from processor import ConnectionProcessor, HubProcessor, Processor


class Factory:
    def __init__(self) -> None:
        self.nbr_drones: int = 0
        self.process_file()

    @staticmethod
    def _parse_restrictions(content: str) -> dict[str, Any]:
        match = re.search(r"\[(.*?)\]", content)
        if not match:
            return {}

        restrictions: dict[str, Any] = {}
        for pair in match.group(1).strip().split():
            if "=" not in pair:
                raise SyntaxError(f"Bad metadata format: '{pair}'")
            key, value = pair.split("=", 1)
            restrictions[key] = int(value) if value.isdigit() else value
        return restrictions

    def process_file(self, file_path: str | None = None) -> None:
        path = file_path or (sys.argv[1] if len(sys.argv) > 1 else None)
        if not path:
            print("Error: Not enough args. Use: <programa> <mapa.txt>")
            sys.exit(1)

        try:
            with open(path, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except OSError as e:
            print(f"Something about file path maybe? (error): {e}")
            sys.exit(1)

        nb_drones_parsed = False

        for line_num, line in enumerate(lines, 1):
            clean_line = line.strip()

            if not clean_line or clean_line.startswith("#"):
                continue

            if not nb_drones_parsed:
                if not clean_line.startswith("nb_drones:"):
                    raise SyntaxError(
                            f"Line {line_num}: First functional line must be: 'nb_drones:'"
                    )
                parts = clean_line.split(":")
                if len(parts) != 2 or not parts[1].strip().isdigit():
                    raise SyntaxError(f"Line {line_num}: Incorrect Format 'nb_drones: <int>' ")

                self.nbr_drones = int(parts[1].strip())
                if self.nbr_drones <= 0:
                    raise ValueError(f"Line {line_num}: 'nb_drones' must be > 0")

                nb_drones_parsed = True
                continue

            if ":" not in clean_line:
                raise SyntaxError(f"Line {line_num}: Line not recognised '{clean_line}'")

            tag, content = [p.strip() for p in clean_line.split(":", 1)]
          
            try:
                restrictions = self._parse_restrictions(content)
                base_tokens = content.split("[")[0].strip().split() # ]

                if tag in ("start_hub", "hub", "end_hub"):
                    if len(base_tokens) != 3:
                        raise SyntaxError(
                            f"Line {line_num}: Hub format must be '<name> <x> <y>'"
                        )

                    name, x_str, y_str = base_tokens
                    try:
                        coor = (int(x_str), int(y_str))
                    except ValueError:
                        raise ValueError(f"Line {line_num}: Coor must be ints")

                    if tag in ("start_hub", "end_hub") and "max_drones" not in restrictions:
                        restrictions["max_drones"] = self.nbr_drones

                    HubProcessor(name=name, coor=coor, **restrictions)
                elif tag == "connection":
                    if len(base_tokens) != 1:
                        raise SyntaxError(f"Line {line_num}: Invalid Connection format")

                    ConnectionProcessor(name=base_tokens[0], **restrictions)
                else:
                    raise SyntaxError(f"Line {line_num}: Forbidden tag '{tag}'")

            except (ValueError, SyntaxError) as e:
                print(f"Error processing line {line_num} ({tag}): {e}")
                sys.exit(1)

        if not nb_drones_parsed:
            raise SyntaxError("File does not contain 'nb_drones:' as first line")
        Processor.format()


class Linkers:
    def __init__(self, filepath: str = "data/map.json") -> None:
        self.filepath = filepath
        self.connections()

    def connections(self) -> None:
        net: dict[str, list[str]] = {} 
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)                  
        except OSError as e:
            print(f"File error - {e}")
            sys.exit(1)
            
        for name in data.get('Hub', {}):
            linked_hubs = set()
            
            for conec in data.get('Connections', {}).keys():
                split_conec = conec.split('-')
                
                if name in split_conec:
                    neighbor = split_conec[0] if split_conec[0] != name else split_conec[1]
                    linked_hubs.add(neighbor)
            
            net[name] = list(linked_hubs)
        
        output_path = "data/network.json"
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(net, f, indent=4)
            print(f"Network generated in: {output_path}")
        except OSError as e:
            print(f"Error writing networkin file - {e}")
            sys.exit(1)
