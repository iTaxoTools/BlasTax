from __future__ import annotations

from pathlib import Path
from typing import NamedTuple


class Results(NamedTuple):
    haplotype_stats: Path
    seconds_taken: float
