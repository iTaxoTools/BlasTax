from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import NamedTuple

from itaxotools.blastax.codons import get_codon_tables

CODON_TABLES = get_codon_tables()
READING_FRAMES = [1, 2, 3]


class RemovalMode(Enum):
    trim_after_stop = (
        "Trim after stop",
        "trim sequences at the first stop codon, including the stop codon itself.",
    )
    discard_sequence = (
        "Discard sequence",
        "remove individual sequences that contain stop codons from each FASTA file.",
    )
    discard_file = (
        "Discard file",
        "remove the entire FASTA file if any sequence contains a stop codon.",
    )

    def __init__(self, label: str, description: str):
        self.label = label
        self.description = description

    def __str__(self):
        return self.key


class RemovalResults(NamedTuple):
    output_path: Path
    description: str
    seconds_taken: float
