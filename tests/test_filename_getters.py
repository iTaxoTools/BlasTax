from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import NamedTuple

import pytest

from itaxotools.blastax.core import (
    get_append_filename,
    get_blast_filename,
    get_decont_blast_filename,
    get_decont_sequences_filename,
    get_fasta_prepared_filename,
    get_museo_filename,
    get_output_filename,
)
from itaxotools.blastax.scafos import get_scafos_filename

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


class BlastFilenameTest(NamedTuple):
    input_path: Path
    target_filename: str
    outfmt: int
    timestamp: datetime | None
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
    description: str | None
    timestamp: datetime | None
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
    timestamp: datetime | None
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
    timestamp: datetime | None
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
    description: str | None
    timestamp: datetime | None
    kwargs: dict[str, str]

    def validate(self):
        filename = get_decont_sequences_filename(
            self.input_path,
            self.description,
            self.timestamp,
            **self.kwargs)
        assert filename == self.target_filename


class FastaRenameFilenameTest(NamedTuple):
    input_path: Path
    target_filename: str | None
    timestamp: datetime

    def validate(self):
        filename = get_fasta_prepared_filename(
            self.input_path,
            self.timestamp)
        assert filename == self.target_filename


class ScafosFilenameTest(NamedTuple):
    input_path: Path
    target_filename: str
    timestamp: datetime | None
    kwargs: dict[str, str]

    def validate(self):
        filename = get_scafos_filename(
            self.input_path,
            self.timestamp,
            **self.kwargs)
        assert filename == self.target_filename


class OutputFilenameTest(NamedTuple):
    input_path: Path
    target_filename: str
    suffix: str | None
    description: str | None
    timestamp: datetime | None
    kwargs: dict[str, str]

    def validate(self):
        filename = get_output_filename(
            self.input_path,
            self.suffix,
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

    FastaRenameFilenameTest(Path("some.fa"), "some_prepared.fasta", None),
    FastaRenameFilenameTest(Path("some.fa"), "some_prepared_17070329T061742.fasta", datetime(1707, 3, 29, 6, 17, 42)),

    ScafosFilenameTest(Path("some.fa"), "some_chimeras.fasta", None, {}),
    ScafosFilenameTest(Path("some.fa"), "some_chimeras_17070329T061742.fasta", datetime(1707, 3, 29, 6, 17, 42), {}),
    ScafosFilenameTest(Path("some.fa"), "some_chimeras_fuse_by_filling_gaps.fasta", None, dict(fuse_by_filling_gaps=None)),
    ScafosFilenameTest(Path("some.fa"), "some_chimeras_fuse_by_filling_gaps_17070329T061742.fasta", datetime(1707, 3, 29, 6, 17, 42), dict(fuse_by_filling_gaps=None)),

    OutputFilenameTest(Path("some.fa"), "some.fasta", ".fasta", None, None, {}),
    OutputFilenameTest(Path("some.fa"), "some_test.fa", None, "test", None, {}),
    OutputFilenameTest(Path("some.fa"), "some_17070329T061742.fa", None, None, datetime(1707, 3, 29, 6, 17, 42), {}),
    OutputFilenameTest(Path("some.fa"), "some_foo_42_bar.fa", None, None, None, dict(foo=42, bar=None)),
    OutputFilenameTest(Path("some.fa"), "some_test_foo_42_bar_17070329T061742.fasta", ".fasta", "test", datetime(1707, 3, 29, 6, 17, 42), dict(foo=42, bar=None)),
]


@pytest.mark.parametrize("test", filename_tests)
def test_run_blast(test: NamedTuple):
    test.validate()
