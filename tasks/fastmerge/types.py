from __future__ import annotations

from enum import Enum


class FormatGroup(Enum):
    all = "All files"
    fasta = "FASTA only"
    fastq = "FASTQ only"

    def __str__(self):
        return self._value_
