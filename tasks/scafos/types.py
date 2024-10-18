from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


@dataclass
class TargetPaths:
    chimeras_path: Path

    def __iter__(self):
        return iter(vars(self).values())


@dataclass
class DistanceTargetPaths(TargetPaths):
    distances_path: Path
    means_path: Path


class TagMethodTexts(Enum):
    SpeciesBeforeFirstUnderscore = (
        "species_before_first_underscore",
        "Species before 1st underscore",
        "use 'species' from 'species_specimen_other'",
    )
    SpeciesBeforeSecondUnderscore = (
        "species_before_second_underscore",
        "Species before 2nd underscore",
        "use 'genus_species' from 'genus_species_specimen_other'",
    )
    SpeciesAfterPipe = (
        "species_after_pipe",
        "Species after pipe",
        "for files in the MolD data format, use 'species' from 'seqid|species'",
    )

    def __init__(self, key: str, title: str, description: str):
        self.key = key
        self.title = title
        self.description = description


class AmalgamationMethodTexts(Enum):
    ByMaxLength = (
        "select_by_max_length",
        "Select by maximum length",
        "keep the sequence with maximum number of information",
    )
    ByMinimumDistance = (
        "select_by_min_distance",
        "Select by minimum distance",
        "keep the sequence that is closest to other species in average",
    )
    ByFillingGaps = (
        "fuse_by_filling_gaps",
        "Fuse by filling gaps",
        "keep the most common character of each position",
    )

    def __init__(self, key: str, title: str, description: str):
        self.key = key
        self.title = title
        self.description = description
