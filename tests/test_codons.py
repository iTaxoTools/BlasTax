from __future__ import annotations

from typing import NamedTuple

import pytest

from itaxotools.blastax.codons import (
    are_counts_ambiguous,
    count_stop_codons_for_all_frames_in_sequence,
    find_stop_codon_in_sequence,
    smart_trim_sequence,
)


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


class CountStopCodonsTest(NamedTuple):
    sequence: str
    table_id: int
    counts: tuple[int, int, int]
    positions: tuple[int, int, int]

    def validate(self) -> None:
        counts, positions = count_stop_codons_for_all_frames_in_sequence(
            self.sequence,
            self.table_id,
        )

        assert counts == self.counts
        assert positions == self.positions


class SmartTrimTest(NamedTuple):
    sequence: str
    table_id: int
    trim_stop: bool
    trim_end: bool
    expected: str

    def validate(self) -> None:
        counts, positions = count_stop_codons_for_all_frames_in_sequence(
            self.sequence,
            self.table_id,
        )
        seq = smart_trim_sequence(
            self.sequence,
            counts,
            positions,
            self.trim_stop,
            self.trim_end,
        )

        assert seq == self.expected


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
    FindStopCodonTest("a", 1, 1, -1),
    FindStopCodonTest("ac", 1, 1, -1),
    FindStopCodonTest("acg", 1, 1, -1),
    FindStopCodonTest("tga", 1, 1, 0),
    FindStopCodonTest("ctga", 1, 2, 1),
    FindStopCodonTest("cctga", 1, 3, 2),
    FindStopCodonTest("cCtGa", 1, 3, 2),
    FindStopCodonTest("taa", 2, 1, 0),
]


count_stop_codons_tests = [
    CountStopCodonsTest("", 1, (0, 0, 0), (-1, -1, -1)),
    CountStopCodonsTest("A", 1, (0, 0, 0), (-1, -1, -1)),
    CountStopCodonsTest("AA", 1, (0, 0, 0), (-1, -1, -1)),
    CountStopCodonsTest("AAA", 1, (0, 0, 0), (-1, -1, -1)),
    CountStopCodonsTest("TAG", 1, (1, 0, 0), (0, -1, -1)),
    CountStopCodonsTest("ATAG", 1, (0, 1, 0), (-1, 1, -1)),
    CountStopCodonsTest("AATAG", 1, (0, 0, 1), (-1, -1, 2)),
    CountStopCodonsTest("AAATAG", 1, (1, 0, 0), (3, -1, -1)),
    CountStopCodonsTest("TGA", 2, (0, 0, 0), (-1, -1, -1)),
    CountStopCodonsTest("TAATAGTGA", 1, (3, 0, 0), (0, -1, -1)),
    CountStopCodonsTest("TAACCCTAGCCCAGACCCAGG", 2, (4, 0, 0), (0, -1, -1)),
    CountStopCodonsTest("TAATAGTGA", 1, (3, 0, 0), (0, -1, -1)),
    CountStopCodonsTest("tag", 1, (1, 0, 0), (0, -1, -1)),
    CountStopCodonsTest("atag", 1, (0, 1, 0), (-1, 1, -1)),
    CountStopCodonsTest("aatag", 1, (0, 0, 1), (-1, -1, 2)),
    CountStopCodonsTest("aATAg", 1, (0, 0, 1), (-1, -1, 2)),
]


smart_trim_tests = [
    SmartTrimTest("", 1, False, False, ""),
    SmartTrimTest("", 1, True, True, ""),
    SmartTrimTest("A", 1, False, False, "A"),
    SmartTrimTest("A", 1, True, True, ""),
    SmartTrimTest("AA", 1, False, False, "AA"),
    SmartTrimTest("AA", 1, True, True, ""),
    SmartTrimTest("AAA", 1, False, False, "AAA"),
    SmartTrimTest("AAA", 1, True, True, ""),
    SmartTrimTest("TAG", 1, False, False, "AG"),
    SmartTrimTest("TAG", 1, False, True, ""),
    SmartTrimTest("CTAG", 1, False, False, "CTAG"),
    SmartTrimTest("CTAG", 1, False, True, "CTA"),
    SmartTrimTest("TAATAGAGAGG", 2, False, False, "AATAGAGAGG"),
    SmartTrimTest("TAATAGAGAGG", 2, False, True, "AATAGAGAG"),
    SmartTrimTest("TAATAGAGAGG", 2, True, False, "AAT"),
    SmartTrimTest("TAATAGAGAGG", 2, True, True, "AAT"),
    SmartTrimTest("a", 1, False, False, "a"),
    SmartTrimTest("aa", 1, False, False, "aa"),
    SmartTrimTest("aaa", 1, False, False, "aaa"),
    SmartTrimTest("tag", 1, False, False, "ag"),
    SmartTrimTest("ctag", 1, False, False, "ctag"),
    SmartTrimTest("ctag", 1, False, True, "cta"),
    SmartTrimTest("Ctag", 1, False, True, "Cta"),
]

@pytest.mark.parametrize("test", find_stop_codon_tests)
def test_find_stop_codons(test: FindStopCodonTest) -> None:
    test.validate()


@pytest.mark.parametrize("test", count_stop_codons_tests)
def test_count_stop_codons(test: CountStopCodonsTest) -> None:
    test.validate()


@pytest.mark.parametrize("test", smart_trim_tests)
def test_smart_trim_sequence(test: SmartTrimTest) -> None:
    test.validate()

def test_are_counts_ambiguous() -> None:
    assert are_counts_ambiguous((0, 0, 0))
    assert are_counts_ambiguous((1, 2, 3))
    assert not are_counts_ambiguous((0, 1, 1))
    assert not are_counts_ambiguous((2, 0, 1))
    assert not are_counts_ambiguous((3, 2, 0))
