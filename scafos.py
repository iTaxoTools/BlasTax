from __future__ import annotations

from enum import Enum, auto

from itaxotools.taxi2.sequences import Sequence


class TagMethod(Enum):
    SpeciesAfterPipe = auto()
    SpeciesBeforeFirstUnderscore = auto()
    SpeciesBeforeSecondUnderscore = auto()


def _tag_species_after_pipe(sequence: Sequence) -> Sequence:
    parts = sequence.id.split("|")
    if len(parts) != 2:
        return sequence
    sequence.extras["species"] = parts[1]
    return sequence


def _tag_species_before_first_underscore(sequence: Sequence) -> Sequence:
    parts = sequence.id.split("_")
    if len(parts) < 2:
        return sequence
    sequence.extras["species"] = parts[0]
    return sequence


def _tag_species_before_second_underscore(sequence: Sequence) -> Sequence:
    parts = sequence.id.split("_")
    if len(parts) < 3:
        return sequence
    sequence.extras["species"] = parts[1]
    return sequence


def tag_species_by_method(sequence: Sequence, method: TagMethod) -> Sequence:
    return {
        TagMethod.SpeciesAfterPipe: _tag_species_after_pipe,
        TagMethod.SpeciesBeforeFirstUnderscore: _tag_species_before_first_underscore,
        TagMethod.SpeciesBeforeSecondUnderscore: _tag_species_before_second_underscore,
    }[method](sequence)
