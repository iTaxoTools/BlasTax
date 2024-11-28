from __future__ import annotations

from enum import Enum

from codons import get_codon_tables

CODON_TABLE_VERSION, CODON_TABLES = get_codon_tables()


class TranslationMode(Enum):
    cds = (
        "Coding sequence",
        "search for the translation without any stop or minimal number of stops.",
        "cds",
    )
    cds_stop = (
        "Coding sequence with stop",
        "search for the translation without any stop or minimal number of stops; terminal stops preferred.",
        "cds_stop",
    )
    transscript = (
        "Transcript",
        "search for the longest open reading frame (the longest sequence part without stops).",
        # "Additionally writes nucleotide sequences of the ORF in separate file",
        "transscript",
    )
    all = (
        "All",
        "get all six possible translations.",
        "all",
    )

    def __init__(self, label: str, description: str, key: str):
        self.label = label
        self.description = description
        self.key = key

    def __str__(self):
        return self.description


class ReadingFrame(Enum):
    pass
