from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TargetPaths:
    output_path: Path
    error_log_path: Path

    def __iter__(self):
        return iter(vars(self).values())
