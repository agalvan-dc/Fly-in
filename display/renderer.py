import colorsys
from typing import Any
import json
import math
import sys

import pygame


class Renderer:
    def __init__(self,
                 width: int = 1024,
                 height: int = 768,
                 node_config: str = "data/map.json",
                 ticks: str = "data/log.json") -> None:
        try:
            with open(node_config, "r", encoding="utf-8") as f:
                self.node_config = json.load(f)
            with open(ticks, "r", encoding="utf-8") as f:
                self.ticks = json.load(f)
        except OSError as e:
            print(f"Error reading JSON files: {e}")
            sys.exit(1)

        self.is_playing = False
        self.time_acc = 0.0
        self.tick_duration = 0.8

        self.drone_angles: dict[Any, Any] = {}
        self.drone_colors: dict[Any, Any] = {}

        self.nodes = self.node_config.get("Hub", {})
        self.connections = self.node_config.get("Connections", {})
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        self.compute_scale_and_offset(width, height)
        self.init_drone_colors()
        self.inject_initial_state()

        self.current_idx = 0
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 36)

    def get_start_coor(self) -> tuple[float, float]:
        for name, data in self.nodes.items():
            if name.lower() in ("start", "0", "start_node") or data.get("is_start"):
                return tuple(data["coor"])
        if self.nodes:
            return tuple(next(iter(self.nodes.values()))["coor"])
        return (0.0, 0.0)

    def init_drone_colors(self) -> None:
        all_drone_ids = set()
        for tick_data in self.ticks.values():
            for i, d in enumerate(tick_data):
                all_drone_ids.add(d.get("id", i))

        sorted_ids = sorted(list(all_drone_ids), key=lambda x: str(x))
        total_drones = len(sorted_ids) if sorted_ids else 1

        for idx, d_id in enumerate(sorted_ids):
            hue = (idx / max(total_drones, 1)) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
            self.drone_colors[d_id] = (int(r * 255), int(g * 255), int(b * 255))

    def inject_initial_state(self) -> None:
        start_coor = self.get_start_coor()
        min_k = min(int(k) for k in self.ticks.keys()) if self.ticks else 0
        synthetic_key = str(min_k - 1)

        self.ticks[synthetic_key] = [
            {"id": d_id, "coor": list(start_coor)}
            for d_id in self.drone_colors.keys()
        ]
        self.tick_keys = sorted(int(k) for k in self.ticks.keys())

    def compute_scale_and_offset(self, width: int, height: int) -> None:
        if not self.nodes:
            return

        xs = [data["coor"][0] for data in self.nodes.values()]
        ys = [data["coor"][1] for data in self.nodes.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        map_w = max_x - min_x if (max_x - min_x) > 0 else 1
        map_h = max_y - min_y if (max_y - min_y) > 0 else 1

        margin = 100
        scale_x = (width - margin * 2) / map_w
        scale_y = (height - margin * 2) / map_h

        self.scale = min(scale_x, scale_y)
        self.offset_x = (width - (map_w * self.scale)) / 2 - (min_x * self.scale)
        self.offset_y = (height - (map_h * self.scale)) / 2 - (min_y * self.scale)

    def to_screen(self, x: float, y: float) -> tuple[float, float]:
        return x * self.scale + self.offset_x, y * self.scale + self.offset_y

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_p:
                    self.is_playing = not self.is_playing
                    if self.is_playing and self.current_idx == 0:
                        self.time_acc = 0.0
                elif event.key == pygame.K_j:
                    self.current_idx = max(0, self.current_idx - 1)
                    self.time_acc = 0.0
                elif event.key == pygame.K_k:
                    self.current_idx = min(len(self.tick_keys) - 1,
                                           self.current_idx + 1)
                    self.time_acc = 0.0
                elif event.key == pygame.K_SPACE:
                    self.current_idx = 0
                    self.time_acc = 0.0
                    self.is_playing = False
        return True

    def update(self, dt: float) -> bool:
        dt = min(dt, 0.05)

        if self.is_playing:
            self.time_acc += dt
            while self.time_acc >= self.tick_duration:
                self.time_acc -= self.tick_duration
                if self.current_idx < len(self.tick_keys) - 1:
                    self.current_idx += 1
                else:
                    self.is_playing = False
                    self.time_acc = 0.0
                    break
        return True

    def render_frame(self, window: pygame.Surface, dt: float) -> bool:
        if not self.update(dt):
            return False

        window.fill((15, 15, 20))

        # Conexiones
        for conn_name in self.connections:
            parts = conn_name.split("-")
            if (len(parts) == 2 and parts[0]
               in self.nodes and parts[1] in self.nodes):
                c1 = self.nodes[parts[0]]["coor"]
                c2 = self.nodes[parts[1]]["coor"]
                p1 = self.to_screen(c1[0], c1[1])
                p2 = self.to_screen(c2[0], c2[1])
                pygame.draw.line(window, (80, 100, 120), p1, p2, 4)

        # Nodos
        for node_data in self.nodes.values():
            x, y = node_data["coor"]
            pos = self.to_screen(x, y)
            color = node_data.get("color", (100, 150, 200))
            pygame.draw.circle(window, color, pos, 20)
            pygame.draw.circle(window, (255, 255, 255), pos, 20, 2)

        # Drones
        if self.current_idx < len(self.tick_keys):
            current_tick_str = str(self.tick_keys[self.current_idx])
            drones_current = self.ticks.get(current_tick_str, [])

            next_idx = min(self.current_idx + 1, len(self.tick_keys) - 1)
            next_tick_str = str(self.tick_keys[next_idx])
            drones_next = self.ticks.get(next_tick_str, [])

            next_drones_map = {d.get("id", i): d for i, d in enumerate(drones_next)}
            progress = (min(1.0, max(0.0, self.time_acc / self.tick_duration))
                        if self.is_playing else 0.0)

            for i, d in enumerate(drones_current):
                d_id = d.get("id", i)
                x1, y1 = d["coor"]

                next_d = next_drones_map.get(d_id)
                if (next_d and self.current_idx < len(self.tick_keys) - 1
                   and self.is_playing):
                    x2, y2 = next_d["coor"]
                else:
                    x2, y2 = x1, y1

                if x1 != x2 or y1 != y2:
                    angle = math.atan2(y2 - y1, x2 - x1)
                    self.drone_angles[d_id] = angle
                else:
                    angle = self.drone_angles.get(d_id, math.radians(-90))

                interp_x = x1 + (x2 - x1) * progress
                interp_y = y1 + (y2 - y1) * progress
                pos = self.to_screen(interp_x, interp_y)

                color = self.drone_colors.get(d_id, (255, 255, 255))
                pointer = self.obtain_arrow(pos[0], pos[1], angle=angle, size=13)

                pygame.draw.polygon(window, color, pointer)
                pygame.draw.polygon(window, (10, 10, 15), pointer, 2)

        menu_options = [
            "Controls:",
            "[ P ] Start / Pause",
            "[ J ] Previous Frame",
            "[ K ] Next Frame",
            "[ SPACE ] Restart",
            "[ ESC ] Exit"
        ]

        y_offset = 15
        for text in menu_options:
            text_surface = self.font.render(text, True, (200, 220, 255))
            window.blit(text_surface, (15, y_offset))
            y_offset += 25

        if not self.is_playing and self.current_idx == 0:
            prompt_surface = self.font_large.render("Press [ P ] "
                                                    "to start animation",
                                                    True, (255, 220, 100))
            rect = prompt_surface.get_rect(center=(window.get_width() // 2, 40))
            window.blit(prompt_surface, rect)

        return True

    def obtain_arrow(self,
                     x: float,
                     y: float,
                     angle: float,
                     size: float = 15
                     ) -> list[tuple[float, float]]:
        p_x = x + math.cos(angle) * size
        p_y = y + math.sin(angle) * size
        bl_x = x + math.cos(angle + math.radians(140)) * size
        bl_y = y + math.sin(angle + math.radians(140)) * size
        inner_x = x + math.cos(angle + math.pi) * (size * 0.3)
        inner_y = y + math.sin(angle + math.pi) * (size * 0.3)
        br_x = x + math.cos(angle - math.radians(140)) * size
        br_y = y + math.sin(angle - math.radians(140)) * size
        return [(p_x, p_y), (bl_x, bl_y), (inner_x, inner_y), (br_x, br_y)]
