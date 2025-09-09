from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import NamedTuple


@dataclass
class TargetPaths:
    output_path: Path
    report_path: Path
    error_log_path: Path

    def __iter__(self):
        return iter(vars(self).values())


class CutAdaptAction(Enum):
    trim = ("trim", "trim adapter and up- or downstream sequence")
    retain = ("retain", "trim, but retain adapter")
    mask = ("mask", "replace with 'N' characters")
    lowercase = ("lowercase", "convert to lowercase")
    crop = ("crop", "trim up and downstream sequence")
    none = ("none", "leave unchanged")

    def __init__(self, action: str, description: str):
        self.action = action
        self.description = description
        self.label = f'{str(action+":").ljust(10)} {description.lower().replace("-", " - ")}'


class CutAdaptResults(NamedTuple):
    output_path: Path
    total_reads: int
    reads_with_adapters: int
    failed: list[Path]
    seconds_taken: float

    @property
    def percent(self) -> float:
        if not self.total_reads:
            return 0.0
        return 100 * self.reads_with_adapters / self.total_reads
