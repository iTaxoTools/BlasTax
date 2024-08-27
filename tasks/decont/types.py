from __future__ import annotations

from enum import Enum


class DecontVariable(Enum):
    pident = ("pident", "Percentage of identical matches", 2)
    bitscore = ("bitscore", "Bit score", 3)
    length = ("length", "Alignment length", 4)

    def __init__(self, variable: str, description: str, column: int):
        self.variable = variable
        self.description = description
        self.column = column
