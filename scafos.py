from __future__ import annotations

from collections import Counter
from enum import Enum, auto
from typing import Iterator

from itaxotools.taxi2.sequences import Sequence, Sequences


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


def count_non_gaps(seq: str) -> int:
    counter = Counter(seq)
    gaps = counter["-"]
    gaps += counter["?"]
    gaps += counter["*"]
    return counter.total() - gaps


def fuse_by_max_length(sequences: Iterator[Sequence]) -> Sequences:
    species_dict: dict[str, Sequence] = {}
    species_length: dict[str, Sequence] = {}
    for sequence in sequences:
        species = sequence.extras["species"]
        length = count_non_gaps(sequence.seq)
        if species not in species_dict:
            species_dict[species] = sequence
            species_length[species] = length
            continue
        if length > species_length[species]:
            species_dict[species] = sequence
            species_length[species] = length
    return Sequences(list(species_dict.values()))
