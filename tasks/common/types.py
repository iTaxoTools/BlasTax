from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import NamedTuple


class Results(NamedTuple):
    output_path: Path
    seconds_taken: float


class WarnResults(NamedTuple):
    output_path: Path
    warnings: list[str]
    seconds_taken: float


class BatchResults(NamedTuple):
    output_path: Path
    failed: list[Path]
    seconds_taken: float


class BlastMethod(Enum):
    blastn = ("blastn", "Nucleotide-Nucleotide")
    blastp = ("blastp", "Protein-Protein")
    blastx = ("blastx", "Translated Query-Protein Subject")
    tblastn = ("tblastn", "Protein Query-Translated Subject")
    tblastx = ("tblastx", "Translated Query-Translated Subject")

    def __init__(self, executable: str, description: str):
        self.executable = executable
        self.description = description
        self.label = f'{str(executable+":").ljust(10)} {description.lower().replace("-", " - ")}'


BLAST_OUTFMT_OPTIONS = {
    0: "Pairwise",
    1: "Query-anchored showing identities",
    2: "Query-anchored no identities",
    3: "Flat query-anchored showing identities",
    4: "Flat query-anchored no identities",
    5: "BLAST XML",
    6: "Tabular (TSV)",
    7: "Tabular with comment lines",
    8: "Seqalign (Text ASN.1)",
    9: "Seqalign (Binary ASN.1)",
    10: "Comma-separated values (CSV)",
    11: "BLAST archive (ASN.1)",
    12: "Seqalign (JSON)",
    13: "Multiple-file BLAST JSON",
    14: "Multiple-file BLAST XML2",
    15: "Single-file BLAST JSON",
    16: "Single-file BLAST XML2",
    17: "Sequence Alignment/Map (SAM)",
    18: "Organism Report",
}

BLAST_OUTFMT_SPECIFIERS_TABULAR = {
    "qseqid": "Query Seq-id",
    "qgi": "Query GI",
    "qacc": "Query accession",
    "qaccver": "Query accession.version",
    "qlen": "Query sequence length",
    "sseqid": "Subject Seq-id",
    "sallseqid": "All subject Seq-id(s), separated by a ';'",
    "sgi": "Subject GI",
    "sallgi": "All subject GIs",
    "sacc": "Subject accession",
    "saccver": "Subject accession.version",
    "sallacc": "All subject accessions",
    "slen": "Subject sequence length",
    "qstart": "Start of alignment in query",
    "qend": "End of alignment in query",
    "sstart": "Start of alignment in subject",
    "send": "End of alignment in subject",
    "qseq": "Aligned part of query sequence",
    "sseq": "Aligned part of subject sequence",
    "evalue": "Expect value",
    "bitscore": "Bit score",
    "score": "Raw score",
    "length": "Alignment length",
    "pident": "Percentage of identical matches",
    "nident": "Number of identical matches",
    "mismatch": "Number of mismatches",
    "positive": "Number of positive-scoring matches",
    "gapopen": "Number of gap openings",
    "gaps": "Total number of gaps",
    "ppos": "Percentage of positive-scoring matches",
    "frames": "Query and subject frames separated by a '/'",
    "qframe": "Query frame",
    "sframe": "Subject frame",
    "btop": "Blast traceback operations (BTOP)",
    "staxid": "Subject Taxonomy ID",
    "ssciname": "Subject Scientific Name",
    "scomname": "Subject Common Name",
    "sblastname": "Subject Blast Name",
    "sskingdom": "Subject Super Kingdom",
    "staxids": "unique Subject Taxonomy ID(s), separated by a ';' (in numerical order)",
    "sscinames": "unique Subject Scientific Name(s), separated by a ';'",
    "scomnames": "unique Subject Common Name(s), separated by a ';'",
    "sblastnames": "unique Subject Blast Name(s), separated by a ';' (in alphabetical order)",
    "sskingdoms": "unique Subject Super Kingdom(s), separated by a ';' (in alphabetical order)",
    "stitle": "Subject Title",
    "salltitles": "All Subject Title(s), separated by a '<>'",
    "sstrand": "Subject Strand",
    "qcovs": "Query Coverage Per Subject",
    "qcovhsp": "Query Coverage Per HSP",
    "qcovus": "Query Coverage Per Unique Subject (blastn only)",
}

BLAST_OUTFMT_SPECIFIERS_SAM = {
    "SQ": "Include Sequence Data",
    "SR": "Subject as Reference Seq",
}

BLAST_OUTFMT_SPECIFIERS_TABLE = {
    6: BLAST_OUTFMT_SPECIFIERS_TABULAR,
    7: BLAST_OUTFMT_SPECIFIERS_TABULAR,
    10: BLAST_OUTFMT_SPECIFIERS_TABULAR,
    # 17: BLAST_OUTFMT_SPECIFIERS_SAM,
}
