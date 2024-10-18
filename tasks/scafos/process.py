from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import cast

from ..common.types import Results
from .types import AmalgamationMethodTexts, DistanceTargetPaths, TargetPaths


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    input_paths: list[Path],
    output_path: Path,
    amalgamation_method: AmalgamationMethodTexts,
    save_reports: bool,
    append_timestamp: bool,
    append_configuration: bool,
) -> Results:
    from itaxotools import abort, get_feedback, progress_handler

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{amalgamation_method=}")
    print(f"{save_reports=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_paths)
    timestamp = datetime.now() if append_timestamp else None

    configuration: dict[str, str] = {}
    if append_configuration:
        configuration[amalgamation_method.key] = None

    target_paths_list = [
        get_target_paths(path, output_path, amalgamation_method, timestamp, configuration) for path in input_paths
    ]

    if any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (path, target_paths) in enumerate(zip(input_paths, target_paths_list)):
        progress_handler(f"{i}/{total}", i, 0, total)
        execute_single(
            input_path=path,
            target_paths=target_paths,
            amalgamation_method=amalgamation_method,
            save_reports=save_reports,
        )
    progress_handler(f"{total}/{total}", total, 0, total)

    tf = perf_counter()

    return Results(output_path, tf - ts)


def execute_single(
    input_path: Path,
    target_paths: TargetPaths,
    amalgamation_method: AmalgamationMethodTexts,
    save_reports: bool,
) -> Results:
    from scafos import AmalgamationMethod, get_fuse_method_callable

    amalgamation_method = {
        AmalgamationMethodTexts.ByMaxLength: AmalgamationMethod.ByMaxLength,
        AmalgamationMethodTexts.ByMinimumDistance: AmalgamationMethod.ByMinimumDistance,
        AmalgamationMethodTexts.ByFillingGaps: AmalgamationMethod.ByFillingGaps,
    }[amalgamation_method]

    output_path = target_paths.chimeras_path

    extra_args = {}
    if save_reports:
        if amalgamation_method == AmalgamationMethod.ByMinimumDistance:
            target_paths = cast(DistanceTargetPaths, target_paths)
            extra_args = dict(distance_report=target_paths.distances_path, mean_report=target_paths.means_path)

    callable = get_fuse_method_callable(amalgamation_method)
    # callable(input_path, **extra_args)

    print(callable)
    print(input_path)
    print(output_path)
    print(extra_args)


def get_target_paths(
    input_path: Path,
    output_path: Path,
    amalgamation_method: AmalgamationMethodTexts,
    timestamp: datetime | None,
    configuration: dict[str, str],
) -> TargetPaths:
    from scafos import get_scafos_filename

    chimeras_path = output_path / get_scafos_filename(input_path, timestamp=timestamp, **configuration)

    if amalgamation_method == AmalgamationMethodTexts.ByMinimumDistance:
        distances_path = chimeras_path.with_stem(chimeras_path.stem + "_distances").with_suffix(".txt")
        means_path = chimeras_path.with_stem(chimeras_path.stem + "_means").with_suffix(".txt")
        return DistanceTargetPaths(
            chimeras_path=chimeras_path,
            distances_path=distances_path,
            means_path=means_path,
        )

    return TargetPaths(
        chimeras_path=chimeras_path,
    )
