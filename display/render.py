import pygame

from .renderer import Renderer


class Display:
    def __init__(self,
                 width: int = 1024,
                 height: int = 768,
                 node_config: str = "data/map.json",
                 ticks: str = "data/log.json") -> None:
        pygame.init()
        pygame.display.set_caption("Drone Simulation Visualizer")
        window = pygame.display.set_mode((width, height))

        self.renderer = Renderer(width=width,
                                 height=height,
                                 node_config=node_config,
                                 ticks=ticks)
        clock = pygame.time.Clock()

        running = True
        while running:
            dt = clock.tick(60) / 1000.0
            running = self.renderer.handle_events()
            if not running:
                break

            self.renderer.render_frame(window, dt)
            pygame.display.flip()

        pygame.quit()
