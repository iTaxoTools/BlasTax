from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from itaxotools.blastax.codons import get_codon_tables

CODON_TABLES = get_codon_tables()


class TrimResults(NamedTuple):
    output_path: Path
    description: str
    seconds_taken: float
