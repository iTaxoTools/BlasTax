from __future__ import annotations

from enum import Enum


class Position(Enum):
    Beginning = "beginning"
    End = "end"

    def __str__(self):
        return self._value_
