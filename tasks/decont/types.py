from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class DecontVariable(Enum):
    pident = ("pident", "Percentage of identical matches", 2)
    bitscore = ("bitscore", "Bit score", 3)
    length = ("length", "Alignment length", 4)

    def __init__(self, variable: str, description: str, column: int):
        self.variable = variable
        self.description = description
        self.column = column

    @classmethod
    def from_column(cls, column: int) -> DecontVariable:
        for item in cls:
            if item.column == column:
                return item


@dataclass
class TargetPaths:
    blasted_ingroup_path: Path
    ingroup_sequences_path: Path
    blasted_outgroup_path: Path
    outgroup_sequences_path: Path

    def __iter__(self):
        return iter(vars(self).values())
