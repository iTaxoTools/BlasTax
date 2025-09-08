from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


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
