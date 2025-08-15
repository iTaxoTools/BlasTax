from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass
class TargetPaths:
    output_path: Path
    error_log_path: Path

    def __iter__(self):
        return iter(vars(self).values())


class AdjustDirection(Enum):
    No = 0, "No", None
    Yes = 1, "Yes", "adjustdirection"
    Accurately = 2, "Accurately", "adjustdirectionaccurately"

    def __init__(self, key: str, title: str, option):
        self.key = key
        self.title = title
        self.option = option


class AlignmentStrategy(Enum):
    Auto = (
        "auto",
        "Auto",
        "choose between FFT-NS-1 or G-INS-i, based on data size",
    )
    FFTNS1 = (
        "fftns1",
        "FFT-NS-1",
        "progressive method that uses a rough guide tree; very fast but very rough",
    )
    GINSi = (
        "ginsi",
        "G-INS-i",
        "iterative refinement, suitable for sequences with global homology; very slow",
    )

    def __init__(self, key: str, title: str, description: str):
        self.key = key
        self.title = title
        self.description = description
