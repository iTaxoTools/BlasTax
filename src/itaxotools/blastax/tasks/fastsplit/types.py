from __future__ import annotations

from enum import Enum


class FileFormat(Enum):
    text = "Text", "text"
    fasta = "FASTA", "fasta"
    fastq = "FASTQ", "fastq"

    def __init__(self, description: str, key: str):
        self.description = description
        self.key = key

    def __str__(self):
        return self.description


class SplitOption(Enum):
    max_size = "Maximum size", "maxsize"
    split_n = "Number of output files", "split_n"
    pattern_identifier = "Seq. identifier pattern", "seqid"
    pattern_sequence = "Seq. motif pattern", "sequence"

    def __init__(self, description: str, key: str):
        self.description = description
        self.key = key

    def __str__(self):
        return self.description
