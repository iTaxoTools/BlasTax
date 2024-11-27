from __future__ import annotations

from enum import Enum

from codons import get_codon_tables

CODON_TABLE_VERSION, CODON_TABLES = get_codon_tables()


class InputType(Enum):
    cds = "Searching for the translation without any stop or minimal number of stops", "cds"
    cds_stop = (
        "Searching for the translation without any stop or minimal number of stops; terminal stops preferred",
        "cds_stop",
    )
    transscript = (
        "Searching for the longest open reading frame (the longest sequence part without stops), writing orf into FASTA-File. Additionally writes nucleotide sequences of the ORF in separate file",
        "transscript",
    )
    all = "All six possible translations", "all"

    def __init__(self, description: str, key: str):
        self.description = description
        self.key = key

    def __str__(self):
        return self.description


class ReadingFrame(Enum):
    pass
