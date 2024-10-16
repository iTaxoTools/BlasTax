from typing import NamedTuple

import pytest

from itaxotools.taxi2.sequences import Sequence, Sequences
from scafos import (
    FuseMethod,
    TagMethod,
    count_non_gaps,
    get_fuse_method_callable,
    tag_species_by_method,
)


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
    method: FuseMethod
    input: Sequences
    expected: Sequences

    def validate(self):
        output = get_fuse_method_callable(self.method)(self.input)
        generated_list = list(output)
        expected_list = list(self.expected)
        assert len(expected_list) == len(generated_list)
        for sequence in expected_list:
            assert sequence in generated_list


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
        FuseMethod.ByMaxLength,
        Sequences([]),
        Sequences([]),
    ),
    FuseTest(
        FuseMethod.ByMaxLength,
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
        FuseMethod.ByMinimumDistance,
        Sequences([]),
        Sequences([]),
    ),
    FuseTest(
        FuseMethod.ByMinimumDistance,
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
]


@pytest.mark.parametrize("test", tag_tests)
def test_tag_species(test: TagTest):
    test.validate()


@pytest.mark.parametrize("test", fuse_tests)
def test_fuse_sequences(test: FuseTest):
    test.validate()
