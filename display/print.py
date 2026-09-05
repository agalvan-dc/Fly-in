import os
import sys
from time import sleep

from questionary import Choice, Separator, Style, select


def print_animated(text: str,
                   ansi_code: str = "\033[1;32m",
                   delay: float = 0.05) -> None:
    """
    Print text to terminal character-by-character with an animation delay.

    Args:
        text: The string content to print.
        ansi_code: ANSI escape sequence for formatting/color.
        delay: Delay in seconds between each printed character.
    """
    print(ansi_code, end="", flush=True)
    for char in text:
        print(char, end="", flush=True)
        sleep(delay)

    print("\033[0m")


def loading(text: str | Exception,
            color_code: str = "\033[0m", delay: float = 0.03) -> None:
    """
    Display a animated loading text sequence on the current terminal line.

    Args:
        text: Text string or exception message to display.
        color_code: ANSI escape sequence for styling.
        delay: Delay in seconds between characters.
    """
    print(f"\r\033[2K{color_code}", end="", flush=True)

    for char in str(text):
        print(char, end="", flush=True)
        sleep(delay)

    print("\033[0m", end="", flush=True)
    sleep(0.5)


def print_frames() -> None:
    """Animate a terminal loading screen sequence with frame transitions."""
    frames = [
        "Toolbar Loading [o     ]",
        "Toolbar Loading [ o    ]",
        "Toolbar Loading [  o   ]",
        "Toolbar Loading [   o  ]",
        "Toolbar Loading [    o ]",
        "Toolbar Loading [     o]",
    ]
    for frame in frames:
        print("\033[H\033[J" + frame, end="", flush=True)
        sleep(0.2)
    sys.stdout.write("\033[H\033[J")
    menu = [
        "O       ",
        "Op      ",
        "Opt     ",
        "Opti    ",
        "Optio   ",
        "Option  ",
        "Options ",
        "Options:",
        "Options: \n1",
        "Options: \n1.",
        "Options: \n1. m",
        "Options: \n1. ma",
        "Options: \n1. map",
        "Options: \n1. map s",
        "Options: \n1. map se",
        "Options: \n1. map sel",
        "Options: \n1. map sele",
        "Options: \n1. map selec",
        "Options: \n1. map select",
        "Options: \n1. map selecti",
        "Options: \n1. map selectio",
        "Options: \n1. map selection",
        "Options: \n1. map selection \n2",
        "Options: \n1. map selection \n2.",
        "Options: \n1. map selection \n2. E",
        "Options: \n1. map selection \n2. Ex",
        "Options: \n1. map selection \n2. Exi",
        "Options: \n1. map selection \n2. Exit",
        "Options: \n1. map selection \n2. Exit t",
        "Options: \n1. map selection \n2. Exit th",
        "Options: \n1. map selection \n2. Exit the",
        "Options: \n1. map selection \n2. Exit the s",
        "Options: \n1. map selection \n2. Exit the si",
        "Options: \n1. map selection \n2. Exit the sim",
        "Options: \n1. map selection \n2. Exit the simu",
        "Options: \n1. map selection \n2. Exit the simul",
        "Options: \n1. map selection \n2. Exit the simula",
        "Options: \n1. map selection \n2. Exit the simulat",
        "Options: \n1. map selection \n2. Exit the simulati",
        "Options: \n1. map selection \n2. Exit the simulatio",
        "Options: \n1. map selection \n2. Exit the simulation",
        "Options: \n1. map selection \n2. Exit the simulation",
        "Options: \n1. map selection \n2. Exit the simulatio",
        "Options: \n1. map selection \n2. Exit the simulati",
        "Options: \n1. map selection \n2. Exit the simulat",
        "Options: \n1. map selection \n2. Exit the simula",
        "Options: \n1. map selection \n2. Exit the simul",
        "Options: \n1. map selection \n2. Exit the simu",
        "Options: \n1. map selection \n2. Exit the sim",
        "Options: \n1. map selection \n2. Exit the si",
        "Options: \n1. map selection \n2. Exit the s",
        "Options: \n1. map selection \n2. Exit the",
        "Options: \n1. map selection \n2. Exit th",
        "Options: \n1. map selection \n2. Exit t",
        "Options: \n1. map selection \n2. Exit",
        "Options: \n1. map selection \n2. Exi",
        "Options: \n1. map selection \n2. Ex",
        "Options: \n1. map selection \n2. E",
        "Options: \n1. map selection \n2. ",
        "Options: \n1. map selection \n",
        "Options: \n1. map selection",
        "Options: \n1. map selectio",
        "Options: \n1. map selecti",
        "Options: \n1. map select",
        "Options: \n1. map selec",
        "Options: \n1. map sele",
        "Options: \n1. map sel",
        "Options: \n1. map se",
        "Options: \n1. map s",
        "Options: \n1. map",
        "Options: \n1. ma",
        "Options: \n1. m",
        "Options: \n1",
        "Options: \n",
        "Options:",
        "Options",
        "Option",
        "Option: ",
    ]
    for frame in menu:
        print("\033[H\033[J\033[1;94m" + frame, end="", flush=True)
        sleep(0.1)


def print_maps() -> str:
    """
    Prompt user with an interactive terminal menu to select a simulation map.

    Returns:
        The selected map text file path, or an empty string if cancelled.
    """
    blue_style = Style([
        ('question', 'fg:ansiblue bold'),
        ('pointer', 'fg:ansiblue bold'),
        ('highlighted', 'fg:ansiblue'),
        ('selected', 'fg:ansigreen'),
    ])

    options = [
        Separator("=== Easy ==="),
        Choice(title="01_linear_path",      value="easy/01_linear_path"),
        Choice(title="02_simple_fork",      value="easy/02_simple_fork"),
        Choice(title="03_basic_capacity",   value="easy/03_basic_capacity"),
        Choice(title="04_parallel_lanes",   value="easy/04_parallel_lanes"),
        Choice(title="05_zigzag_corridor",  value="easy/05_zigzag_corridor"),
        Choice(title="06_restricted_shortcut",  
               value="easy/06_restricted_shortcut"),

        Separator("\n    === Medium ==="),
        Choice(title="01_dead_end_trap",      value="medium/01_dead_end_trap"),
        Choice(title="02_circular_loop",      value="medium/02_circular_loop"),
        Choice(title="03_priority_puzzle",
               value="medium/03_priority_puzzle"),
        Choice(title="04_double_bottleneck",
               value="medium/04_double_bottleneck"),
        Choice(title="05_traffic_circle",
               value="medium/05_traffic_circle"),
        Choice(title="06_priority_highway",
               value="medium/06_priotiry_highway"),

        Separator("\n    === Hard ==="),
        Choice(title="01_maze_nightmare",     value="hard/01_maze_nightmare"),
        Choice(title="02_capacity_hell",      value="hard/02_capacity_hell"),
        Choice(title="03_ultimate_challenge",
               value="hard/03_ultimate_challenge"),
        Choice(title="04_gridlock_lsbyrinth",
               value="hard/04_gridlock_labyrinth"),
        Choice(title="05_hazard_funnel",    value="hard/05_hazard_funnel"),
        Choice(title="06_ring_of_fire",    value="hard/06_ring_of_fire"),

        Separator("\n    === Challenger ==="),
        Choice(title="01_the_impossible_dream",
               value="challenger/01_the_impossible_dream"),
        Choice(title="02_the_needle_eye",
               value="challenger/02_the_needle_eye"),
        Choice(title="03_labyrinth_of_shadows",
               value="challenger/03_labyrinth_of_shadows"),
        Choice(title="04_hypercube_collapse",
               value="challenger/04_hypercube_collapse"),
        Choice(title="05_ouroboros_protocol",
               value="challenger/05_ouroboros_protocol"),
        Choice(title="06_the_false_prophet",
               value="challenger/06_the_false_prophet"),
        Choice(title="07_absolute_zero",
               value="challenger/07_absolute_zero"),
        Choice(title="08_fractal_deadlock",
               value="challenger/08_fractal_deadlock"),
        Choice(title="09_the_gordian_knot",
               value="challenger/09_the_gordian_knot"),
        Choice(title="10_temporal_stagger",
               value="challenger/10_temporal_stagger"),

        Choice(title="99_omega_singularity",
               value="challenger/99_omega_singularity"),
    ]

    selected_route = select(
        "Map selection",
        choices=options,
        qmark="",
        pointer="->",
        style=blue_style
    ).ask()

    if not selected_route:
        print("\033[32mOperation cancelled.\033[0m")
        return ""

    final_route = os.path.join("maps", f"{selected_route.strip()}.txt")
    return final_route
