from __future__ import annotations

from enum import Enum

from codons import get_codon_tables

CODON_TABLE_VERSION, CODON_TABLES = get_codon_tables()
READING_FRAMES = {"autodetect": "Autodetect"} | {str(i): str(i) for i in range(1, 7)}


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
        "search for the longest Open Reading Drame (the longest sequence part without stops).",
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
        return self.key
