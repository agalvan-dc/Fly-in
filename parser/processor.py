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
    """Abstract base class managing network map ingestion and JSON export."""

    map: ClassVar[Config] = {'Hub': {}, 'Connections': {}}

    @abstractmethod
    def ingest(self) -> None:
        """Abstract method to ingest model attributes into shared map data."""
        pass

    @classmethod
    def format(cls, filename: str = "data/map.json") -> None:
        """
        Write the populated map configuration to a formatted JSON file.

        Args:
            filename: Target output path for the generated map file.
        """
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(cls.map, file, indent=4)


class HubProcessor(BaseModel, Processor):
    """Validate and process individual hub configuration entries."""

    name: str = Field(pattern=r"^[^-]*$")
    coor: tuple[int, int]
    color: str | None = None
    max_drones: int | None = None
    zone: str | None = None
    is_start: bool | None = None
    is_end: bool | None = None

    def __init__(self, **data: Any) -> None:
        """
        Initialize and ingest hub parameters.

        Args:
            **data: Key-value attributes for hub data initialization.
        """
        super().__init__(**data)
        self.ingest()

    @field_validator("coor", mode='before')
    @classmethod
    def parse_tuple(cls, value: Any) -> Any:
        """
        Parse raw coordinate strings into integer coordinate tuples.

        Args:
            value: Coordinate value as string or tuple.

        Returns:
            A tuple of two integer coordinates.

        Raises:
            ValueError: If coordinates cannot be extracted from string.
        """
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
        """
        Validate color format, capacity limits, and zone classifications.

        Returns:
            Self after validation completes.

        Raises:
            ValueError: If capacity or zone parameters are invalid.
        """
        if self.color is not None and self.color != "rainbow":
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
        """Store hub attributes into the shared map dictionary."""
        data = self.model_dump(exclude={"name"}, exclude_none=True, mode="json")
        self.map['Hub'][self.name] = data


class ConnectionProcessor(BaseModel, Processor):
    """Validate and process node connection entries."""

    name: str = Field(pattern=r"^[^-]+-[^-]+$")
    max_link_capacity: int = Field(default=1)

    def __init__(self, **data: Any) -> None:
        """
        Initialize and ingest connection parameters.

        Args:
            **data: Key-value attributes for connection initialization.
        """
        super().__init__(**data)
        self.ingest()

    @model_validator(mode='after')
    def verify(self) -> 'ConnectionProcessor':
        """
        Validate that maximum link capacity is valid.

        Returns:
            Self after validation.

        Raises:
            ValueError: If link capacity is less than 1.
        """
        if self.max_link_capacity < 1:
            raise ValueError("Max Link Capacity cant be less than 1")
        return self

    def ingest(self) -> None:
        """Store connection data into the shared map dictionary."""
        data = self.model_dump(exclude={"name"}, mode="json")
        self.map["Connections"][self.name] = data
