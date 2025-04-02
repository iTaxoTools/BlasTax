from __future__ import annotations

from enum import Enum


class Direction(Enum):
    Beginning = "beginning"
    End = "end"

    def __str__(self):
        return self._value_
