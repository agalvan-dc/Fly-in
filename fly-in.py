#!/usr/bin/env python3

from parser import parser
from algorithmic import StateMachine, Orchestrator
from display import print_animated, loading, print_frames, print_maps, Display
from rich.console import Console
from time import sleep
import sys



def main() -> None:

    sys.stdout.write("\033[H\033[J") # ]
    console = Console()
    if len(sys.argv) == 1:
        print_animated("Welcome to the drone simulation...")
        print_frames()
        option = input()
        while option != "2":
            match option:
                case "1":
                    loading("Select map: ")
                    filepath = print_maps()
                    loading("Parsing...")
                    print()
                    sleep(0.2)
                    try:
                        parser(filepath)
                    except (ValueError, OSError, SyntaxError) as e:
                        loading(e, "\033[1;31m") # ]
                        print()
                        sys.exit(1)
                    loading("Initializing the construct...")
                    print()
                    try:
                        StateMachine(Orchestrator())
                    except (OSError, ValueError) as e:
                        loading(e, "\033[1;31;3") # ]
                        sys.exit(1)
                    loading("Displaying...")
                    try:
                        Display()
                        loading("Display ended. Choose again: ")
                        option = input()
                        sys.stdout.write("\033[H\033[J") # ]
                    except OSError as e:
                        loading(e, "\033[1;31m") # ]
                        sys.exit(1)
                case "2":
                    print_animated("Exiting the simulation...")
                    sys.exit(0)
                case _:
                    console.print("Not a valid option", style="bold red")
                    print()
    else:
        tasks = [parser(), StateMachine(Orchestrator(), Display())]

        with console.status("[bold greed]Working on pathfinding...",
                            spinner="arrow3"):
            while tasks:
                task = tasks.pop(0)
                sleep(1)
                console.log(f"{task} completed)")
    



if __name__  == "__main__":
    main()

