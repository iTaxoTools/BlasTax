from __future__ import annotations

from collections import Counter, defaultdict
from enum import Enum, auto
from itertools import groupby
from pathlib import Path
from typing import Iterator, NamedTuple

from itaxotools.taxi2.distances import Distance, DistanceHandler, DistanceMetric
from itaxotools.taxi2.handlers import FileHandler
from itaxotools.taxi2.pairs import SequencePair, SequencePairs
from itaxotools.taxi2.sequences import Sequence, Sequences


class TagMethod(Enum):
    SpeciesAfterPipe = auto()
    SpeciesBeforeFirstUnderscore = auto()
    SpeciesBeforeSecondUnderscore = auto()


class DistanceGroups(NamedTuple):
    key: str
    others: list[Distance]


class AggregatedDistances(NamedTuple):
    sequence: Sequence
    species_distances: dict[str, list[float]]


class AggregatedMean(NamedTuple):
    sequence: Sequence
    mean: float


class MeanGroups(NamedTuple):
    key: str
    items: list[AggregatedMean]


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


def fuse_by_max_length(sequences: Sequences) -> Sequences:
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


def drop_identical_pairs(pairs: Iterator[SequencePair]) -> Iterator[SequencePair]:
    for pair in pairs:
        if pair.x.id != pair.y.id:
            yield pair


def calculate_distances(pairs: Iterator[SequencePair]) -> Iterator[Distance]:
    metric = DistanceMetric.Uncorrected()
    for x, y in pairs:
        yield metric.calculate(x, y)


def report_distances(distances: Iterator[Distance], path: Path) -> Iterator[Distance]:
    with DistanceHandler.Linear.WithExtras(path, "w") as file:
        for distance in distances:
            file.write(distance)
            yield distance


def group_distances(distances: Iterator[Distance]) -> Iterator[DistanceGroups]:
    keyfunc = lambda distance: distance.x.id
    for left, group in groupby(distances, keyfunc):
        yield DistanceGroups(left, list(group))


def aggregate_groups(groups: Iterator[DistanceGroups]) -> Iterator[AggregatedDistances]:
    for group in groups:
        distance_dict: dict[str, list[float]] = defaultdict(list)
        for distance in group.others:
            if distance.d is None:
                continue
            distance_dict[distance.y.extras["species"]].append(distance.d)
        sequence = group.others[0].x
        assert sequence.id == group.key
        yield AggregatedDistances(sequence, distance_dict)


def calculate_mean(data: Iterator[AggregatedDistances]) -> Iterator[AggregatedMean]:
    for item in data:
        species = item.sequence.extras["species"]
        if species in item.species_distances:
            del item.species_distances[species]
        means: list[float] = []
        for distances in item.species_distances.values():
            mean = sum(distances) / len(distances)
            means.append(mean)
        mean_of_means = sum(means) / len(means)
        yield AggregatedMean(item.sequence, mean_of_means)


def report_means(means: Iterator[AggregatedMean], path: Path) -> Iterator[AggregatedMean]:
    with FileHandler.Tabular.Tabfile(path, "w", columns=["id", "species", "mean"]) as file:
        for item in means:
            file.write((item.sequence.id, item.sequence.extras["species"], str(item.mean)))
            yield item


def group_species(data: Iterator[AggregatedMean]) -> Iterator[DistanceGroups]:
    keyfunc = lambda item: item.sequence.extras["species"]
    data = sorted(data, key=keyfunc)
    for key, group in groupby(data, keyfunc):
        yield MeanGroups(key, list(group))


def keep_minimum_mean(groups: Iterator[MeanGroups]) -> Iterator[Sequence]:
    for group in groups:
        selected = min(group.items, key=lambda item: item.mean)
        yield selected.sequence


def fuse_by_min_distance(sequences: Sequences) -> Sequences:
    pairs = SequencePairs.fromProduct(sequences, sequences)
    pairs = drop_identical_pairs(pairs)
    distances = calculate_distances(pairs)
    distances = report_distances(distances, "report_distances.txt")
    groups = group_distances(distances)
    aggregated = aggregate_groups(groups)
    means = calculate_mean(aggregated)
    means = report_means(means, "report_means.txt")
    groups = group_species(means)
    sequences = keep_minimum_mean(groups)

    return Sequences(list(sequences))
