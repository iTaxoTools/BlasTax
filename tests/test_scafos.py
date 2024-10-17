from pathlib import Path
from typing import NamedTuple

import pytest

from itaxotools.taxi2.sequences import Sequence, Sequences
from scafos import (
    AmalgamationMethod,
    TagMethod,
    count_non_gaps,
    fuse_by_filling_gaps,
    fuse_by_minimum_distance,
    get_fuse_method_callable,
    tag_species_by_method,
)

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


class FuseTest(NamedTuple):
    method: AmalgamationMethod
    input: Sequences
    expected: Sequences

    def validate(self):
        output = get_fuse_method_callable(self.method)(self.input)
        assert_sequences_equal(output, self.expected)


tag_tests = [
    TagTest(TagMethod.SpeciesAfterPipe, Sequence("id1", "ATC"), Sequence("id1", "ATC")),
    TagTest(TagMethod.SpeciesAfterPipe, Sequence("id1", "ATC", {"voucher": "X"}), Sequence("id1", "ATC", {"voucher": "X"})),
    TagTest(TagMethod.SpeciesAfterPipe, Sequence("id1|species1", "ATC"), Sequence("id1|species1", "ATC", {"species": "species1"})),

    TagTest(TagMethod.SpeciesBeforeFirstUnderscore, Sequence("id1", "ATC"), Sequence("id1", "ATC")),
    TagTest(TagMethod.SpeciesBeforeFirstUnderscore, Sequence("id1", "ATC", {"voucher": "X"}), Sequence("id1", "ATC", {"voucher": "X"})),
    TagTest(TagMethod.SpeciesBeforeFirstUnderscore, Sequence("species1_id1", "ATC"), Sequence("species1_id1", "ATC", {"species": "species1"})),
    TagTest(TagMethod.SpeciesBeforeFirstUnderscore, Sequence("species1_id1_xyz", "ATC"), Sequence("species1_id1_xyz", "ATC", {"species": "species1"})),

    TagTest(TagMethod.SpeciesBeforeSecondUnderscore, Sequence("id1", "ATC"), Sequence("id1", "ATC")),
    TagTest(TagMethod.SpeciesBeforeSecondUnderscore, Sequence("id1", "ATC", {"voucher": "X"}), Sequence("id1", "ATC", {"voucher": "X"})),
    TagTest(TagMethod.SpeciesBeforeSecondUnderscore, Sequence("genus1_species1_id1", "ATC"), Sequence("genus1_species1_id1", "ATC", {"species": "species1"})),
    TagTest(TagMethod.SpeciesBeforeSecondUnderscore, Sequence("genus1_species1_id1_xyz", "ATC"), Sequence("genus1_species1_id1_xyz", "ATC", {"species": "species1"})),
]


gap_tests = [
    GapTest("ACGT", 4),
    GapTest("ACGT-", 4),
    GapTest("ACGT?", 4),
    GapTest("ACGT*", 4),
    GapTest("ACGT*?-", 4),
    GapTest("ACGT*?-acgt", 8),
]


fuse_tests = [
    FuseTest(
        AmalgamationMethod.ByMaxLength,
        Sequences([]),
        Sequences([]),
    ),
    FuseTest(
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
    FuseTest(
        AmalgamationMethod.ByMinimumDistance,
        Sequences([]),
        Sequences([]),
    ),
    FuseTest(
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
    FuseTest(
        AmalgamationMethod.ByFillingGaps,
        Sequences([]),
        Sequences([]),
    ),
    FuseTest(
        AmalgamationMethod.ByFillingGaps,
        Sequences([
            Sequence("id1", "AC--", {"species": "X"}),
            Sequence("id2", "--GT", {"species": "X"}),
            Sequence("id3", "---A", {"species": "Y"}),
            Sequence("id4", "T---", {"species": "Y"}),
        ]),
        Sequences([
            Sequence("X_id1_id2", "ACGT", {"species": "X"}),
            Sequence("Y_id3_id4", "T--A", {"species": "Y"}),
        ]),
    ),
]


@pytest.mark.parametrize("test", tag_tests)
def test_tag_species(test: TagTest):
    test.validate()


@pytest.mark.parametrize("test", fuse_tests)
def test_fuse_sequences(test: FuseTest):
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

    output = fuse_by_minimum_distance(sequences_input, distance_report_output, mean_report_output)

    assert_sequences_equal(output, sequences_expected)
    assert_file_equals(distance_report_output, distance_report_expected)
    assert_file_equals(mean_report_output, mean_report_expected)


def test_fuse_by_filling_gaps_uneven_lengths():
    with pytest.raises(Exception, match="'Y'"):
        sequences = Sequences([
            Sequence("id1", "ACGT", {"species": "X"}),
            Sequence("id2", "ACGT", {"species": "X"}),
            Sequence("id3", "TGCA", {"species": "Y"}),
            Sequence("id4", "TGGTGGT", {"species": "Y"}),
        ])
        fuse_by_filling_gaps(sequences)
