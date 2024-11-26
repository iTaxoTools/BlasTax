from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from enum import Enum, auto
from itertools import groupby
from pathlib import Path
from typing import Callable, Iterator, NamedTuple

from core import get_info_suffix, get_timestamp_suffix
from itaxotools.taxi2.distances import Distance, DistanceHandler, DistanceMetric
from itaxotools.taxi2.handlers import FileHandler
from itaxotools.taxi2.pairs import SequencePair, SequencePairs
from itaxotools.taxi2.sequences import Sequence, Sequences

GAP_CHARACTERS = "-?* "


class TagMethod(Enum):
    SpeciesAfterPipe = auto()
    SpeciesBeforeFirstUnderscore = auto()
    SpeciesBeforeSecondUnderscore = auto()


class AmalgamationMethod(Enum):
    ByMaxLength = auto()
    ByMinimumDistance = auto()
    ByFillingGaps = auto()
    ByTrimmingParalogs = auto()


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
        raise Exception(f"Could not extract species from identifier: {repr(sequence.id)}")
    sequence = Sequence(sequence.id, sequence.seq, dict(sequence.extras))
    sequence.extras["species"] = parts[1]
    return sequence


def _tag_species_before_first_underscore(sequence: Sequence) -> Sequence:
    parts = sequence.id.split("_")
    if len(parts) < 2:
        raise Exception(f"Could not extract species from identifier: {repr(sequence.id)}")
    sequence = Sequence(sequence.id, sequence.seq, dict(sequence.extras))
    sequence.extras["species"] = parts[0]
    return sequence


def _tag_species_before_second_underscore(sequence: Sequence) -> Sequence:
    parts = sequence.id.split("_")
    if len(parts) < 3:
        raise Exception(f"Could not extract species from identifier: {repr(sequence.id)}")
    sequence = Sequence(sequence.id, sequence.seq, dict(sequence.extras))
    sequence.extras["species"] = "_".join(parts[:2])
    return sequence


def tag_species_by_method(sequence: Sequence, method: TagMethod) -> Sequence:
    return {
        TagMethod.SpeciesAfterPipe: _tag_species_after_pipe,
        TagMethod.SpeciesBeforeFirstUnderscore: _tag_species_before_first_underscore,
        TagMethod.SpeciesBeforeSecondUnderscore: _tag_species_before_second_underscore,
    }[method](sequence)


def count_non_gaps(seq: str) -> int:
    counter = Counter(seq)
    gaps = sum(counter[gap] for gap in GAP_CHARACTERS)
    return counter.total() - gaps


def select_by_max_length(sequences: Sequences) -> Sequences:
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


def _drop_identical_pairs(pairs: Iterator[SequencePair]) -> Iterator[SequencePair]:
    for pair in pairs:
        if pair.x.id != pair.y.id:
            yield pair


def _calculate_distances(pairs: Iterator[SequencePair]) -> Iterator[Distance]:
    metric = DistanceMetric.Uncorrected()
    for x, y in pairs:
        yield metric.calculate(x, y)


def _report_distances(distances: Iterator[Distance], path: Path) -> Iterator[Distance]:
    with DistanceHandler.Linear.WithExtras(path, "w") as file:
        for distance in distances:
            file.write(distance)
            yield distance


def _group_distances_by_left_id(distances: Iterator[Distance]) -> Iterator[DistanceGroups]:
    keyfunc = lambda distance: distance.x.id
    for left, group in groupby(distances, keyfunc):
        yield DistanceGroups(left, list(group))


def _aggregate_distance_groups(groups: Iterator[DistanceGroups]) -> Iterator[AggregatedDistances]:
    for group in groups:
        distance_dict: dict[str, list[float]] = defaultdict(list)
        for distance in group.others:
            if distance.d is None:
                continue
            distance_dict[distance.y.extras["species"]].append(distance.d)
        sequence = group.others[0].x
        assert sequence.id == group.key
        yield AggregatedDistances(sequence, distance_dict)


def _calculate_means(data: Iterator[AggregatedDistances]) -> Iterator[AggregatedMean]:
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


def _report_means(means: Iterator[AggregatedMean], path: Path) -> Iterator[AggregatedMean]:
    with FileHandler.Tabular.Tabfile(path, "w", columns=["id", "species", "mean"]) as file:
        for item in means:
            file.write((item.sequence.id, item.sequence.extras["species"], str(item.mean)))
            yield item


def _group_means_by_species(data: Iterator[AggregatedMean]) -> Iterator[DistanceGroups]:
    keyfunc = lambda item: item.sequence.extras["species"]
    data = sorted(data, key=keyfunc)
    for key, group in groupby(data, keyfunc):
        yield MeanGroups(key, list(group))


def _keep_minimum_mean(groups: Iterator[MeanGroups]) -> Iterator[Sequence]:
    for group in groups:
        selected = min(group.items, key=lambda item: item.mean)
        yield selected.sequence


def select_by_minimum_distance(
    sequences: Sequences,
    distance_report: Path = None,
    mean_report: Path = None,
) -> Sequences:
    pairs = SequencePairs.fromProduct(sequences, sequences)
    pairs = _drop_identical_pairs(pairs)
    distances = _calculate_distances(pairs)

    if distance_report is not None:
        distances = _report_distances(distances, distance_report)

    groups = _group_distances_by_left_id(distances)
    aggregated = _aggregate_distance_groups(groups)
    means = _calculate_means(aggregated)

    if mean_report is not None:
        means = _report_means(means, mean_report)

    groups = _group_means_by_species(means)
    sequences = _keep_minimum_mean(groups)

    return Sequences(list(sequences))


def _group_sequences_by_species(data: Sequences) -> Iterator[tuple[str, list[Sequence]]]:
    keyfunc = lambda item: item.extras["species"]
    data = sorted(data, key=keyfunc)
    for species, group in groupby(data, keyfunc):
        yield species, list(group)


def _get_most_common_character(characters: Iterator[str]) -> str:
    counter = Counter(characters)
    for gap in GAP_CHARACTERS:
        del counter[gap]
    common = counter.most_common(1)
    if not common:
        return GAP_CHARACTERS[0]
    return common[0][0]


def _assemble_sequence_from_most_common_characters(seqs: list[str]) -> str:
    if not all(len(s) == len(seqs[0]) for s in seqs):
        return None
    sequence = "".join(_get_most_common_character(characters) for characters in zip(*seqs))
    return sequence


def _aggregate_sequence_groups_by_filling_gaps(groups: Iterator[tuple[str, list[Sequence]]]) -> Iterator[Sequences]:
    for species, group in groups:
        # ids = [sequence.id for sequence in group]
        seqs = [sequence.seq for sequence in group]
        id = species + "_chimera"
        seq = _assemble_sequence_from_most_common_characters(seqs)
        if seq is None:
            raise Exception(f"Not all sequences are of the same length for species: {repr(species)}")
        yield Sequence(id, seq, extras=dict(species=species))


def fuse_by_filling_gaps(sequences: Sequences) -> Sequences:
    groups = _group_sequences_by_species(sequences)
    sequences = _aggregate_sequence_groups_by_filling_gaps(groups)
    return Sequences(list(sequences))


def get_amalgamation_method_callable(method: AmalgamationMethod) -> Callable:
    return {
        AmalgamationMethod.ByMaxLength: select_by_max_length,
        AmalgamationMethod.ByMinimumDistance: select_by_minimum_distance,
        AmalgamationMethod.ByFillingGaps: fuse_by_filling_gaps,
        AmalgamationMethod.ByTrimmingParalogs: select_by_excluding_paralogs,
    }[method]


def get_scafos_filename(
    input_path: Path,
    timestamp: datetime | None = None,
    **kwargs,
) -> str:
    path = input_path.with_suffix(".fasta")
    path = path.with_stem(path.stem + "_chimeras")

    info = get_info_suffix(**kwargs)
    path = path.with_stem(path.stem + info)

    if timestamp is not None:
        strftime = get_timestamp_suffix(timestamp)
        path = path.with_stem(path.stem + strftime)
    return path.name


def get_overlapping_positions(a: str, b: str, exclude: str = GAP_CHARACTERS) -> list[int]:
    if len(a) != len(b):
        raise Exception(f"Sequences must have the same length: {repr(a)}, {repr(b)}")
    return [i for i in range(len(a)) if a[i] == b[i] and not (a[i] in exclude or b[i] in exclude)]


def get_characters_in_positions(s: str, positions: list[int]) -> str:
    return "".join(s[i] for i in positions)


def select_by_excluding_paralogs(sequences: Sequences):
    #     groups = _group_sequences_by_species(sequences)
    #     groups = list(groups)

    #     for species, group in groups:
    #         for a, b in combinations(group, 2):
    #             if a.seq == b.seq:
    #                 print(species, a.id, b.id, "IDENTICAL")
    #                 continue
    #             positions = get_overlapping_positions(a.seq, b.seq)
    #             print(">", species, a.id, b.id, positions)
    #             for other_species, other_group in groups:
    #                 if other_species == species:
    #                     continue

    #     assert False

    return Sequences([])
