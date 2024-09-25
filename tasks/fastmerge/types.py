from __future__ import annotations

from enum import Enum


class FormatGroup(Enum):
    all = "All files"
    fasta = "Process only FASTA"
    fastq = "Process only FASTQ"

    def __str__(self):
        return self._value_
