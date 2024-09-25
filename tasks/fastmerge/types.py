from __future__ import annotations

from enum import Enum


class FormatGroup(Enum):
    all = "All files", None
    fasta = "FASTA only", {".fas", ".fasta"}
    fastq = "FASTQ only", {".fq", ".fastq"}

    def __init__(self, text: str, types: set | None):
        self.text = text
        self.types = types

    def __str__(self):
        return self.text
