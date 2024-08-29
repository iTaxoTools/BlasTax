from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import pytest

from core import (
    get_append_filename,
    get_blast_filename,
    get_decont_blast_filename,
    get_decont_sequences_filename,
    get_museo_filename,
)

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class BlastFilenameTest(NamedTuple):
    input_path: Path
    target_filename: str
    outfmt: int
    timestamp: datetime
    kwargs: dict[str, str]

    def validate(self):
        filename = get_blast_filename(
            self.input_path,
            self.outfmt,
            self.timestamp,
            **self.kwargs)
        assert filename == self.target_filename


class DecontBlastFilenameTest(NamedTuple):
    input_path: Path
    target_filename: str
    description: str
    timestamp: datetime
    kwargs: dict[str, str]

    def validate(self):
        filename = get_decont_blast_filename(
            self.input_path,
            self.description,
            self.timestamp,
            **self.kwargs)
        assert filename == self.target_filename


class AppendFilenameTest(NamedTuple):
    input_path: Path
    target_filename: str
    timestamp: datetime
    kwargs: dict[str, str]

    def validate(self):
        filename = get_append_filename(
            self.input_path,
            self.timestamp,
            **self.kwargs)
        assert filename == self.target_filename


class MuseoFilenameTest(NamedTuple):
    input_path: Path
    target_filename: str
    timestamp: datetime
    kwargs: dict[str, str]

    def validate(self):
        filename = get_museo_filename(
            self.input_path,
            self.timestamp,
            **self.kwargs)
        assert filename == self.target_filename


class DecontSequencesFilenameTest(NamedTuple):
    input_path: Path
    target_filename: str
    description: str
    timestamp: datetime
    kwargs: dict[str, str]

    def validate(self):
        filename = get_decont_sequences_filename(
            self.input_path,
            self.description,
            self.timestamp,
            **self.kwargs)
        assert filename == self.target_filename


filename_tests = [
    BlastFilenameTest(Path("some.fa"), "some.txt", 0, None, {}),
    BlastFilenameTest(Path("some.fasta"), "some.txt", 0, None, {}),
    BlastFilenameTest(Path("some.fastq"), "some.txt", 0, None, {}),

    BlastFilenameTest(Path("some.fa"), "some.tsv", 6, None, {}),
    BlastFilenameTest(Path("some.fa"), "some.csv", 10, None, {}),

    BlastFilenameTest(Path("some.fa"), "some_17070329T061742.txt", 0, datetime(1707, 3, 29, 6, 17, 42), {}),
    BlastFilenameTest(Path("some.fa"), "some_20240830T000000.txt", 0, datetime(2024, 8, 30, 0, 0, 0), {}),

    BlastFilenameTest(Path("some.fa"), "some_evalue_0.1.txt", 0, None, dict(evalue=0.1)),
    BlastFilenameTest(Path("some.fa"), "some_blastn.txt", 0, None, {"blastn": None}),
    BlastFilenameTest(Path("some.fa"), "some_method_blastn_evalue_0.1_columns_seqid_sseqid_pident.txt", 0, None, dict(method="blastn", evalue=0.1, columns="seqid_sseqid_pident")),
    BlastFilenameTest(Path("some.fa"), "some_evalue_0.1_17070329T061742.txt", 0, datetime(1707, 3, 29, 6, 17, 42), dict(evalue=0.1)),

    DecontBlastFilenameTest(Path("some.fa"), "some_ingroup.tsv", "ingroup", None, {}),
    DecontBlastFilenameTest(Path("some.fa"), "some_outgroup.tsv", "outgroup", None, {}),
    DecontBlastFilenameTest(Path("some.fa"), "some_ingroup_17070329T061742.tsv", "ingroup", datetime(1707, 3, 29, 6, 17, 42), {}),
    DecontBlastFilenameTest(Path("some.fa"), "some_ingroup_evalue_0.1.tsv", "ingroup", None, dict(evalue=0.1)),
    DecontBlastFilenameTest(Path("some.fa"), "some_ingroup_evalue_0.1_17070329T061742.tsv", "ingroup", datetime(1707, 3, 29, 6, 17, 42), dict(evalue=0.1)),

    AppendFilenameTest(Path("some.fa"), "some_with_blast_matches.fasta", None, {}),
    AppendFilenameTest(Path("some.fa"), "some_with_blast_matches_17070329T061742.fasta", datetime(1707, 3, 29, 6, 17, 42), {}),
    AppendFilenameTest(Path("some.fa"), "some_with_blast_matches_evalue_0.1_single.fasta", None, dict(evalue=0.1, single=None)),
    AppendFilenameTest(Path("some.fa"), "some_with_blast_matches_evalue_0.1_multiple_length_42_pident_97.321.fasta", None, dict(evalue=0.1, multiple=None, length=42, pident=97.321)),
    AppendFilenameTest(Path("some.fa"), "some_with_blast_matches_evalue_0.1_17070329T061742.fasta", datetime(1707, 3, 29, 6, 17, 42), dict(evalue=0.1)),

    MuseoFilenameTest(Path("some.fa"), "some_museo.fasta", None, {}),
    MuseoFilenameTest(Path("some.fa"), "some_museo_17070329T061742.fasta", datetime(1707, 3, 29, 6, 17, 42), {}),
    MuseoFilenameTest(Path("some.fa"), "some_museo_evalue_0.1_single.fasta", None, dict(evalue=0.1, single=None)),
    MuseoFilenameTest(Path("some.fa"), "some_museo_evalue_0.1_multiple_length_42_pident_97.321.fasta", None, dict(evalue=0.1, multiple=None, length=42, pident=97.321)),
    MuseoFilenameTest(Path("some.fa"), "some_museo_evalue_0.1_17070329T061742.fasta", datetime(1707, 3, 29, 6, 17, 42), dict(evalue=0.1)),

    DecontSequencesFilenameTest(Path("some.fa"), "some_decontaminated.fasta", "decontaminated", None, {}),
    DecontSequencesFilenameTest(Path("some.fa"), "some_contaminants.fasta", "contaminants", None, {}),
    DecontSequencesFilenameTest(Path("some.fa"), "some_decontaminated_17070329T061742.fasta", "decontaminated", datetime(1707, 3, 29, 6, 17, 42), {}),
    DecontSequencesFilenameTest(Path("some.fa"), "some_decontaminated_evalue_0.1_single.fasta", "decontaminated", None, dict(evalue=0.1, single=None)),
    DecontSequencesFilenameTest(Path("some.fa"), "some_decontaminated_evalue_0.1_multiple_length_42_pident_97.321.fasta", "decontaminated", None, dict(evalue=0.1, multiple=None, length=42, pident=97.321)),
    DecontSequencesFilenameTest(Path("some.fa"), "some_decontaminated_evalue_0.1_17070329T061742.fasta", "decontaminated", datetime(1707, 3, 29, 6, 17, 42), dict(evalue=0.1)),
]


@pytest.mark.parametrize("test", filename_tests)
def test_run_blast(test: NamedTuple):
    test.validate()
