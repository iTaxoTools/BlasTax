from __future__ import annotations

from typing import NamedTuple

import pytest

from itaxotools.blastax.codons import find_stop_codon_in_sequence


class FindStopCodonTest(NamedTuple):
    sequence: str
    table_id: int
    reading_frame: int
    position: int

    def validate(self) -> None:
        pos = find_stop_codon_in_sequence(
            self.sequence,
            self.table_id,
            self.reading_frame,
        )

        assert pos == self.position


find_stop_codon_tests = [
    FindStopCodonTest("", 1, 1, -1),
    FindStopCodonTest("A", 1, 1, -1),
    FindStopCodonTest("AC", 1, 1, -1),
    FindStopCodonTest("ACG", 1, 1, -1),
    FindStopCodonTest("TGA", 1, 1, 0),
    FindStopCodonTest("TGA", 1, 2, -1),
    FindStopCodonTest("TGA", 1, 3, -1),
    FindStopCodonTest("CTGA", 1, 1, -1),
    FindStopCodonTest("CTGA", 1, 2, 1),
    FindStopCodonTest("CTGA", 1, 3, -1),
    FindStopCodonTest("CCTGA", 1, 1, -1),
    FindStopCodonTest("CCTGA", 1, 2, -1),
    FindStopCodonTest("CCTGA", 1, 3, 2),
    FindStopCodonTest("TAA", 1, 1, 0),
    FindStopCodonTest("TAG", 1, 1, 0),
    FindStopCodonTest("AGG", 1, 1, -1),
    FindStopCodonTest("AGA", 1, 1, -1),
    FindStopCodonTest("AGG", 2, 1, 0),
    FindStopCodonTest("AGA", 2, 1, 0),
    FindStopCodonTest("TAA", 2, 1, 0),
    FindStopCodonTest("TAG", 2, 1, 0),
    FindStopCodonTest("TGA", 2, 1, -1),
]


@pytest.mark.parametrize("test", find_stop_codon_tests)
def test_fastq_to_fasta(test: FindStopCodonTest) -> None:
    test.validate()
