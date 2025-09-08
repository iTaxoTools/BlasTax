from datetime import datetime
from pathlib import Path
from time import perf_counter
from traceback import print_exc

from ..common.types import BatchResults
from .types import AdjustDirection, AlignmentStrategy, TargetPaths


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.utils  # noqa


def execute(
    work_dir: Path,
    input_paths: list[Path],
    output_path: Path,
    strategy: AlignmentStrategy,
    adjust_direction: AdjustDirection,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{strategy=}")
    print(f"{adjust_direction=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_paths)
    failed: list[Path] = []

    timestamp = datetime.now() if append_timestamp else None
    configuration: dict[str, str] = {}
    if append_configuration:
        configuration[strategy.key] = None
        if adjust_direction.option:
            configuration[adjust_direction.option] = None

    target_paths_list = [
        get_target_paths(input_path, output_path, timestamp, configuration) for input_path in input_paths
    ]

    if any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (input_path, target_paths) in enumerate(zip(input_paths, target_paths_list)):
        progress_handler(f"Processing file {i+1}/{total}: {input_path.name}", i, 0, total)
        try:
            single_work_dir = work_dir / input_path.name
            single_work_dir.mkdir()
            execute_single(
                work_dir=single_work_dir,
                input_path=input_path,
                output_path=target_paths.output_path,
                strategy=strategy,
                adjust_direction=adjust_direction,
            )
        except Exception as e:
            if total == 1:
                raise e
            with open(target_paths.error_log_path, "w") as f:
                print_exc(file=f)
            failed.append(input_path)

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_path, failed, tf - ts)


def execute_single(
    work_dir: Path,
    input_path: Path,
    output_path: Path,
    strategy: AlignmentStrategy,
    adjust_direction: AdjustDirection,
):
    from itaxotools.mafftpy import MultipleSequenceAlignment

    task = MultipleSequenceAlignment(input_path)
    task.vars.set_strategy(strategy.key)
    task.vars.set_adjust_direction(adjust_direction.key)
    task.target = work_dir

    task.start()
    task.fetch(output_path)


def get_target_paths(
    input_path: Path,
    output_dir: Path,
    timestamp: datetime | None,
    configuration: dict[str, str],
) -> TargetPaths:
    from itaxotools.blastax.core import get_error_filename, get_output_filename

    output_path = output_dir / get_output_filename(
        input_path=input_path,
        suffix=".fasta",
        description="aligned",
        timestamp=timestamp,
        **configuration,
    )
    error_log_path = output_dir / get_error_filename(output_path)

    return TargetPaths(
        output_path=output_path,
        error_log_path=error_log_path,
    )
