from typing import NamedTuple

import pytest

from itaxotools.taxi2.sequences import Sequence
from scafos import TagMethod, tag_species_by_method


class TagTest(NamedTuple):
    method: TagMethod
    input: Sequence
    expected: Sequence

    def validate(self):
        output = tag_species_by_method(self.input, self.method)
        assert output == self.expected


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


@pytest.mark.parametrize("test", tag_tests)
def test_tag_species(test: TagTest):
    test.validate()
