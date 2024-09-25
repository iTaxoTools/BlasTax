from __future__ import annotations

from enum import Enum


class FormatGroup(Enum):
    all = "All files", None
    fasta = "FASTA only", {".fas", ".fasta"}
    fastq = "FASTQ only", {".fq", ".fastq"}

    def __init__(self, description: str, types: set | None):
        self.description = description
        self.types = types

    def __str__(self):
        return self.description
