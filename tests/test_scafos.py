from pathlib import Path
from typing import NamedTuple

import pytest

from itaxotools.blastax.scafos import (
    GAP_CHARACTERS,
    AmalgamationMethod,
    TagMethod,
    count_non_gaps,
    fuse_by_filling_gaps,
    get_amalgamation_method_callable,
    get_characters_in_positions,
    get_overlapping_positions,
    select_by_minimum_distance,
    tag_species_by_method,
)
from itaxotools.taxi2.sequences import Sequence, Sequences

from .pytest_utils import assert_file_equals

TEST_DATA_DIR = Path(__file__).parent / Path(__file__).stem


def assert_sequences_equal(output_sequences: Sequences, expected_sequences: Sequences):
    generated_list = list(output_sequences)
    expected_list = list(expected_sequences)
    assert len(expected_list) == len(generated_list)
    for sequence in expected_list:
        assert sequence in generated_list


class TagTest(NamedTuple):
    method: TagMethod
    input: Sequence
    expected: Sequence

    def validate(self):
        output = tag_species_by_method(self.input, self.method)
        assert output == self.expected


class GapTest(NamedTuple):
    input: str
    expected: int

    def validate(self):
        length = count_non_gaps(self.input)
        assert length == self.expected


class AmalgamationTest(NamedTuple):
    method: AmalgamationMethod
    input: Sequences
    expected: Sequences
    kwargs: dict = {}

    def validate(self):
        output = get_amalgamation_method_callable(self.method)(self.input, **self.kwargs)
        assert_sequences_equal(output, self.expected)


class OverlapTest(NamedTuple):
    a: str
    b: str
    expected: list[int]
    exclude: str = GAP_CHARACTERS

    def validate(self):
        output = get_overlapping_positions(self.a, self.b, self.exclude)
        assert output == self.expected


class PositionTest(NamedTuple):
    s: str
    pos: list[int]
    expected: str

    def validate(self):
        output = get_characters_in_positions(self.s, self.pos)
        assert output == self.expected



tag_tests = [
    TagTest(TagMethod.SpeciesAfterPipe, Sequence("id1|species1", "ATC"), Sequence("id1|species1", "ATC", {"species": "species1"})),

    TagTest(TagMethod.SpeciesBeforeFirstUnderscore, Sequence("species1_id1", "ATC"), Sequence("species1_id1", "ATC", {"species": "species1"})),
    TagTest(TagMethod.SpeciesBeforeFirstUnderscore, Sequence("species1_id1_xyz", "ATC"), Sequence("species1_id1_xyz", "ATC", {"species": "species1"})),

   TagTest(TagMethod.SpeciesBeforeSecondUnderscore, Sequence("genus1_species1_id1", "ATC"), Sequence("genus1_species1_id1", "ATC", {"species": "genus1_species1"})),
    TagTest(TagMethod.SpeciesBeforeSecondUnderscore, Sequence("genus1_species1_id1_xyz", "ATC"), Sequence("genus1_species1_id1_xyz", "ATC", {"species": "genus1_species1"})),
]


tag_tests_bad = [
    TagTest(TagMethod.SpeciesAfterPipe, Sequence("id1", "ATC"), Sequence("id1", "ATC")),
    TagTest(TagMethod.SpeciesAfterPipe, Sequence("id1", "ATC", {"voucher": "X"}), Sequence("id1", "ATC", {"voucher": "X"})),

    TagTest(TagMethod.SpeciesBeforeFirstUnderscore, Sequence("id1", "ATC"), Sequence("id1", "ATC")),
    TagTest(TagMethod.SpeciesBeforeFirstUnderscore, Sequence("id1", "ATC", {"voucher": "X"}), Sequence("id1", "ATC", {"voucher": "X"})),

    TagTest(TagMethod.SpeciesBeforeSecondUnderscore, Sequence("id1", "ATC"), Sequence("id1", "ATC")),
    TagTest(TagMethod.SpeciesBeforeSecondUnderscore, Sequence("id1", "ATC", {"voucher": "X"}), Sequence("id1", "ATC", {"voucher": "X"})),

]


gap_tests = [
    GapTest("ACGT", 4),
    GapTest("ACGT-", 4),
    GapTest("ACGT?", 4),
    GapTest("ACGT*", 4),
    GapTest("ACGT*?-", 4),
    GapTest("ACGT*?-acgt", 8),
]


amalgamation_tests = [
    AmalgamationTest(
        AmalgamationMethod.ByMaxLength,
        Sequences([]),
        Sequences([]),
    ),
    AmalgamationTest(
        AmalgamationMethod.ByMaxLength,
        Sequences([
            Sequence("id1", "AC--", {"species": "X"}),
            Sequence("id2", "ACGT", {"species": "X"}),
            Sequence("id3", "ACGT", {"species": "Y"}),
            Sequence("id4", "ACG?", {"species": "Y"}),
        ]),
        Sequences([
            Sequence("id2", "ACGT", {"species": "X"}),
            Sequence("id3", "ACGT", {"species": "Y"}),
        ]),
    ),
    AmalgamationTest(
        AmalgamationMethod.ByMinimumDistance,
        Sequences([]),
        Sequences([]),
    ),
    AmalgamationTest(
        AmalgamationMethod.ByMinimumDistance,
        Sequences([
            Sequence("id1", "ACGT", {"species": "X"}),
            Sequence("id2", "ACGT", {"species": "X"}),
            Sequence("id3", "TGCA", {"species": "Y"}),
            Sequence("id4", "TGGT", {"species": "Y"}),
        ]),
        Sequences([
            Sequence("id1", "ACGT", {"species": "X"}),
            Sequence("id4", "TGGT", {"species": "Y"}),
        ]),
    ),
    AmalgamationTest(
        AmalgamationMethod.ByFillingGaps,
        Sequences([]),
        Sequences([]),
    ),
    AmalgamationTest(
        AmalgamationMethod.ByFillingGaps,
        Sequences([
            Sequence("id1", "AC--", {"species": "X"}),
            Sequence("id2", "--GT", {"species": "X"}),
            Sequence("id3", "---A", {"species": "Y"}),
            Sequence("id4", "T-?-", {"species": "Y"}),
        ]),
        Sequences([
            Sequence("X_chimera", "ACGT", {"species": "X"}),
            Sequence("Y_chimera", "T--A", {"species": "Y"}),
        ]),
        dict(ambiguous=False),
    ),
    AmalgamationTest(
        AmalgamationMethod.ByFillingGaps,
        Sequences([
            Sequence("id1", "AC--", {"species": "X"}),
            Sequence("id2", "--GT", {"species": "X"}),
            Sequence("id3", "AAAA-NVVVMMA", {"species": "Y"}),
            Sequence("id4", "CCC--AAAAAT-", {"species": "Y"}),
            Sequence("id5", "GG-----CT---", {"species": "Y"}),
            Sequence("id6", "T----------B", {"species": "Y"}),
        ]),
        Sequences([
            Sequence("X_chimera", "ACGT", {"species": "X"}),
            Sequence("Y_chimera", "NVMA-NVVNMHN", {"species": "Y"}),
        ]),
        dict(ambiguous=True),
    ),
    AmalgamationTest(
        AmalgamationMethod.ByDiscardingOutliers,
        Sequences([]),
        Sequences([]),
    ),
    AmalgamationTest(
        AmalgamationMethod.ByDiscardingOutliers,
        Sequences([
            Sequence("id1", "ACGT", {"species": "X"}),
            Sequence("id2", "ACGA", {"species": "X"}),
            Sequence("id3", "ACTT", {"species": "Y"}),
        ]),
        Sequences([
            Sequence("X_chimera", "ACGT", {"species": "X"}),
            Sequence("Y_chimera", "ACTT", {"species": "Y"}),
        ]),
        dict(outlier_factor=1.5)
    ),
    AmalgamationTest(
        AmalgamationMethod.ByDiscardingOutliers,
        Sequences([
            Sequence("id1", "ACGT", {"species": "X"}),
            Sequence("id2", "ACGA", {"species": "X"}),
            Sequence("id3", "ACTT", {"species": "Y"}),
        ]),
        Sequences([
            Sequence("X_chimera", "ACGW", {"species": "X"}),
            Sequence("Y_chimera", "ACTT", {"species": "Y"}),
        ]),
        dict(outlier_factor=2.0, ambiguous=True)
    ),
    AmalgamationTest(
        AmalgamationMethod.ByDiscardingOutliers,
        Sequences([
            Sequence("id1", "AC--", {"species": "X"}),
            Sequence("id2", "AG--", {"species": "X"}),
            Sequence("id3", "--AT", {"species": "Y"}),
        ]),
        Sequences([
            Sequence("X_chimera", "AS--", {"species": "X"}),
            Sequence("Y_chimera", "--AT", {"species": "Y"}),
        ]),
        dict(outlier_factor=1.5, ambiguous=True)
    ),
]

overlap_tests = [
    OverlapTest("ATCG", "ATCG", [0, 1, 2, 3]),
    OverlapTest("ATCG", "A-*G", [0, 3]),
    OverlapTest("ATCG", "GCTA", []),
    OverlapTest("ATCG", "A-NG", [0, 3], exclude="-N"),
]


overlap_tests_bad = [
    OverlapTest("ATCG", "ATC", [0, 1, 2]),
]


position_tests = [
    PositionTest("ATCG", [0, 1, 2, 3], "ATCG"),
    PositionTest("ATCG", [0, 1, 3], "ATG"),
    PositionTest("ATCG", [2], "C"),
    PositionTest("ATCG", [], ""),
]


@pytest.mark.parametrize("test", tag_tests)
def test_tag_species(test: TagTest):
    test.validate()


@pytest.mark.parametrize("test", tag_tests_bad)
def test_tag_species_bad(test: TagTest):
    with pytest.raises(Exception, match="Could not extract species from identifier"):
        test.validate()


@pytest.mark.parametrize("test", amalgamation_tests)
def test_fuse_sequences(test: AmalgamationTest):
    test.validate()


@pytest.mark.parametrize("test", overlap_tests)
def test_overlap(test: OverlapTest):
    test.validate()


@pytest.mark.parametrize("test", overlap_tests_bad)
def test_overlap_bad(test: TagTest):
    with pytest.raises(Exception, match="Sequences must have the same length"):
        test.validate()


@pytest.mark.parametrize("test", position_tests)
def test_position(test: PositionTest):
    test.validate()


def test_fuse_by_min_reports(tmp_path: Path):
    distance_report_output = tmp_path / "distance_report.txt"
    mean_report_output = tmp_path / "mean_report.txt"
    distance_report_expected = TEST_DATA_DIR / "fuse_by_min_distance_report.txt"
    mean_report_expected = TEST_DATA_DIR / "fuse_by_min_mean_report.txt"

    sequences_input = Sequences([
            Sequence("id1", "ACGT", {"species": "X"}),
            Sequence("id2", "ACGT", {"species": "X"}),
            Sequence("id3", "TGCA", {"species": "Y"}),
            Sequence("id4", "TGGT", {"species": "Y"}),
    ])

    sequences_expected = Sequences([
            Sequence("id1", "ACGT", {"species": "X"}),
            Sequence("id4", "TGGT", {"species": "Y"}),
    ])

    output = select_by_minimum_distance(sequences_input, distance_report_output, mean_report_output)

    assert_sequences_equal(output, sequences_expected)
    assert_file_equals(distance_report_output, distance_report_expected)
    assert_file_equals(mean_report_output, mean_report_expected)


def test_fuse_by_min_reports_no_overlap():
    with pytest.raises(Exception, match="No overlapping segments.*'X'"):
        sequences = Sequences([
            Sequence("id1", "ACGT----", {"species": "X"}),
            Sequence("id2", "ACGT----", {"species": "X"}),
            Sequence("id3", "----TGCA", {"species": "Y"}),
            Sequence("id4", "----TGGT", {"species": "Y"}),
        ])
        select_by_minimum_distance(sequences)


def test_fuse_by_filling_gaps_uneven_lengths():
    with pytest.raises(Exception, match="same length.*'Y'"):
        sequences = Sequences([
            Sequence("id1", "ACGT", {"species": "X"}),
            Sequence("id2", "ACGT", {"species": "X"}),
            Sequence("id3", "TGCA", {"species": "Y"}),
            Sequence("id4", "TGGTGGT", {"species": "Y"}),
        ])
        fuse_by_filling_gaps(sequences)
