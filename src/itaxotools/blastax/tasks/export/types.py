from __future__ import annotations

from enum import Enum
from typing import NamedTuple


class DatabaseInfo(NamedTuple):
    version: int | None
    db_type: str | None
    has_taxids: bool | None


class OperationMode(Enum):
    database_to_fasta = "Export BLAST database to FASTA file"
    taxid_map_from_database = "Extract taxID map from BLAST database"
    taxid_map_from_fasta = "Extract taxID map from FASTA file"
    kraken_style = "Prepare FASTA for building a Kraken2 database"
    database_check_taxid = "Check BLAST database version and taxID mappings"

    def __init__(self, label):
        self.label = label
