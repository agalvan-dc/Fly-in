#!/usr/bin/env python3

from parser import parser
from algorithmic import StateMachine, orq

def main() -> None:
    parser()
    StateMachine(orq())


if __name__  == "__main__":
    main()

