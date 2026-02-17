from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TargetPaths:
    blast_output_path: Path
    taxo_output_path: Path
    report_path: Path | None
    error_log_path: Path

    def __iter__(self):
        return iter(vars(self).values())
