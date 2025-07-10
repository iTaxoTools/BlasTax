from __future__ import annotations

from enum import Enum


class MatchingRule(Enum):
    word = "First word"
    characters = "First few characters"
    regex = "Regular expression"

    def __str__(self):
        return self._value_
