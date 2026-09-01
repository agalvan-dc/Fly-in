#!/usr/bin/env python3

import sys
from time import sleep

from rich.console import Console

from algorithmic import Orchestrator, StateMachine
from display import Display, loading, print_animated, print_frames, print_maps
from parser import parser


def main() -> None:

    sys.stdout.write("\033[H\033[J")
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
                        loading(e, "\033[1;31m")
                        print()
                        sys.exit(1)
                    loading("Initializing the construct...")
                    print()
                    try:
                        StateMachine(Orchestrator())
                    except (OSError, ValueError) as e:
                        loading(e, "\033[1;31;3")
                        sys.exit(1)
                    loading("Displaying...")
                    try:
                        Display()
                        loading("Display ended. Choose again: ")
                        option = input()
                        sys.stdout.write("\033[H\033[J")
                    except OSError as e:
                        loading(e, "\033[1;31m")
                        sys.exit(1)
                case "2":
                    print_animated("Exiting the simulation...")
                    sys.exit(0)
                case _:
                    console.print("Not a valid option", style="bold red")
                    option = input()
                    print()
    else:
        filepath = sys.argv[1]

        with console.status("[bold green]Parsing map file...", spinner="dots") as status:
            try:
                parser(filepath)
                console.print("[bold green]✔[/bold green] Map parsed successfully")
            except (ValueError, OSError, SyntaxError) as e:
                console.print(f"[bold red]Parsing error:[/bold red] {e}")
                sys.exit(1)

            status.update("[bold cyan]Calculating paths & running state machine...")
            try:
                StateMachine(Orchestrator())
                console.print("[bold green]✔[/bold green] Pathfinding computation completed")
            except (OSError, ValueError) as e:
                console.print(f"[bold red]State machine error:[/bold red] {e}")
                sys.exit(1)

            status.update("[bold yellow]Launching visualizer...")
            sleep(0.3)

        console.print("[bold green]✔[/bold green] Environment ready. Opening Display...")
        try:
            Display()
        except OSError as e:
            console.print(f"[bold red]Display error:[/bold red] {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
