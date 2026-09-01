import json
import re
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar

import pygame
from pydantic import BaseModel, Field, field_validator, model_validator

Config = dict[str, Any]


class Processor(ABC):
    map: ClassVar[Config] = {'Hub': {}, 'Connections': {}}

    @abstractmethod
    def ingest(self) -> None:
        pass

    @classmethod
    def format(cls, filename: str = "data/map.json") -> None:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(cls.map, file, indent=4)


class HubProcessor(BaseModel, Processor):
    name: str = Field(pattern=r"^[^-]*$")
    coor: tuple[int, int]
    color: str | None = None
    max_drones: int | None = None
    zone: str | None = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.ingest()

    @field_validator("coor", mode='before')
    @classmethod
    def parse_tuple(cls, value: Any) -> Any:
        if isinstance(value, str):
            match = re.search(r"(-?\d+)\s+(-?\d+)", value)
            if match:
                return int(match.group(1)), int(match.group(2))
            else:
                raise ValueError(f"Exact coors could "
                                 f"not be resolved from: '{value}'")
        return value

    @model_validator(mode='after')
    def verify(self) -> 'HubProcessor':
        if self.color is not None:
            try:
                pygame.Color(self.color)
            except ValueError:
                print(f"Not a valid color - {self.color}")
                sys.exit(1)
        if self.max_drones is not None and self.max_drones <= 0:
            raise ValueError("Number of drones cant be negative or 0...")
        elif (self.zone
              and self.zone not in
              ["normal", "blocked", "restricted", "priority"]):
            raise ValueError(f"Not a valid zone: '{self.zone}'")
        return self

    def ingest(self) -> None:
        data = self.model_dump(exclude={"name"}, exclude_none=True, mode="json")
        self.map['Hub'][self.name] = data


class ConnectionProcessor(BaseModel, Processor):
    name: str = Field(pattern=r"^[^-]+-[^-]+$")
    max_link_capacity: int = Field(default=1)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.ingest()

    @model_validator(mode='after')
    def verify(self) -> 'ConnectionProcessor':
        if self.max_link_capacity < 1:
            raise ValueError("Max Link Capacity cant be less than 1")
        return self

    def ingest(self) -> None:
        data = self.model_dump(exclude={"name"}, mode="json")
        self.map["Connections"][self.name] = data
