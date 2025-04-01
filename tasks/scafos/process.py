from datetime import datetime
from pathlib import Path
from time import perf_counter
from traceback import print_exc
from typing import cast

from ..common.types import BatchResults
from .types import AmalgamationMethodTexts, DistanceTargetPaths, TagMethodTexts, TargetPaths


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    input_paths: list[Path],
    output_path: Path,
    tag_method: TagMethodTexts,
    amalgamation_method: AmalgamationMethodTexts,
    save_reports: bool,
    fuse_ambiguous: bool,
    outlier_factor: float,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{tag_method.key=}")
    print(f"{amalgamation_method.key=}")
    print(f"{save_reports=}")
    print(f"{fuse_ambiguous=}")
    print(f"{outlier_factor=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_paths)
    failed: list[Path] = []

    timestamp = datetime.now() if append_timestamp else None
    configuration: dict[str, str] = {}
    if append_configuration:
        configuration[tag_method.key] = None
        configuration[amalgamation_method.key] = None
        if amalgamation_method in [AmalgamationMethodTexts.ByFillingGaps, AmalgamationMethodTexts.ByDiscardingOutliers]:
            if fuse_ambiguous:
                configuration["with_ambiguity_codes"] = None
            else:
                configuration["by_most_common_character"] = None
        if amalgamation_method == AmalgamationMethodTexts.ByDiscardingOutliers:
            configuration["outlier_factor"] = f"{outlier_factor:.3f}"

    target_paths_list = [
        get_target_paths(path, output_path, amalgamation_method, timestamp, configuration) for path in input_paths
    ]

    if any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (path, target_paths) in enumerate(zip(input_paths, target_paths_list)):
        progress_handler(f"Processing file {i+1}/{total}: {path.name}", i, 0, total)
        try:
            execute_single(
                input_path=path,
                target_paths=target_paths,
                tag_method=tag_method,
                amalgamation_method=amalgamation_method,
                save_reports=save_reports,
                fuse_ambiguous=fuse_ambiguous,
                outlier_factor=outlier_factor,
            )
        except Exception as e:
            if total == 1:
                raise e
            with open(target_paths.error_log_path, "w") as f:
                print_exc(file=f)
            failed.append(path)

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_path, failed, tf - ts)


def execute_single(
    input_path: Path,
    target_paths: TargetPaths,
    tag_method: TagMethodTexts,
    amalgamation_method: AmalgamationMethodTexts,
    save_reports: bool,
    fuse_ambiguous: bool,
    outlier_factor: float,
):
    from itaxotools.taxi2.file_types import FileFormat
    from itaxotools.taxi2.files import identify_format
    from itaxotools.taxi2.sequences import SequenceHandler, Sequences
    from scafos import AmalgamationMethod, TagMethod, get_amalgamation_method_callable, tag_species_by_method

    tag_method = {
        TagMethodTexts.SpeciesBeforeFirstUnderscore: TagMethod.SpeciesBeforeFirstUnderscore,
        TagMethodTexts.SpeciesBeforeSecondUnderscore: TagMethod.SpeciesBeforeSecondUnderscore,
        TagMethodTexts.SpeciesAfterPipe: TagMethod.SpeciesAfterPipe,
    }[tag_method]

    amalgamation_method = {
        AmalgamationMethodTexts.ByMaxLength: AmalgamationMethod.ByMaxLength,
        AmalgamationMethodTexts.ByMinimumDistance: AmalgamationMethod.ByMinimumDistance,
        AmalgamationMethodTexts.ByFillingGaps: AmalgamationMethod.ByFillingGaps,
        AmalgamationMethodTexts.ByDiscardingOutliers: AmalgamationMethod.ByDiscardingOutliers,
    }[amalgamation_method]

    output_path = target_paths.chimeras_path

    extra_kwargs = {}
    if save_reports:
        if amalgamation_method in [AmalgamationMethod.ByMinimumDistance, AmalgamationMethod.ByDiscardingOutliers]:
            target_paths = cast(DistanceTargetPaths, target_paths)
            extra_kwargs |= dict(distance_report=target_paths.distances_path, mean_report=target_paths.means_path)
    if amalgamation_method in [AmalgamationMethod.ByFillingGaps, AmalgamationMethod.ByDiscardingOutliers]:
        extra_kwargs |= dict(ambiguous=fuse_ambiguous)
    if amalgamation_method == AmalgamationMethod.ByDiscardingOutliers:
        extra_kwargs |= dict(outlier_factor=outlier_factor)

    callable = get_amalgamation_method_callable(amalgamation_method)

    format: FileFormat = identify_format(input_path)
    handler = {
        FileFormat.Fasta: SequenceHandler.Fasta,
        FileFormat.FastQ: SequenceHandler.FastQ,
        FileFormat.Ali: SequenceHandler.Ali,
    }[format]

    sequences = Sequences.fromPath(input_path, handler)
    sequences = Sequences([tag_species_by_method(sequence, tag_method) for sequence in sequences])
    with SequenceHandler.Fasta(output_path, "w", line_width=0) as file:
        for sequence in callable(sequences, **extra_kwargs):
            file.write(sequence)


def get_target_paths(
    input_path: Path,
    output_path: Path,
    amalgamation_method: AmalgamationMethodTexts,
    timestamp: datetime | None,
    configuration: dict[str, str],
) -> TargetPaths:
    from core import get_error_filename
    from scafos import get_scafos_filename

    error_log_path = output_path / get_error_filename(input_path, timestamp=timestamp)

    chimeras_path = output_path / get_scafos_filename(input_path, timestamp=timestamp, **configuration)

    if amalgamation_method in [AmalgamationMethodTexts.ByMinimumDistance, AmalgamationMethodTexts.ByDiscardingOutliers]:
        distances_path = chimeras_path.with_stem(chimeras_path.stem + "_distances").with_suffix(".tsv")
        means_path = chimeras_path.with_stem(chimeras_path.stem + "_means").with_suffix(".tsv")
        return DistanceTargetPaths(
            chimeras_path=chimeras_path,
            distances_path=distances_path,
            means_path=means_path,
            error_log_path=error_log_path,
        )

    return TargetPaths(
        chimeras_path=chimeras_path,
        error_log_path=error_log_path,
    )
