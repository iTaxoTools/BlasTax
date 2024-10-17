from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass
class TargetPaths:
    blast_output_path: Path
    appended_output_path: Path

    def __iter__(self):
        return iter(vars(self).values())


class AmalgamationMethodTexts(Enum):
    ByMaxLength = "Select by maximum length", "keep the sequence with maximum number of information"
    ByMinimumDistance = "Select by minimum distance", "keep the sequence that is closest to other species"
    ByFillingGaps = "Fuse by filling gaps", "keep the most common character of each position"

    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description
