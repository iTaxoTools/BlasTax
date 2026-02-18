from __future__ import annotations

from enum import Enum


class OperationMode(Enum):
    database_to_fasta = "Export BLAST database to FASTA file"
    taxid_mapping_from_database = "Extract taxID map from BLAST database"
    database_check_taxid = "Check BLAST database for taxID information"
    taxid_mapping_from_fasta = "Extract taxID map from FASTA file"
    kraken_style = "Add taxIDs to FASTA (Kraken format)"

    def __init__(self, label):
        self.label = label
