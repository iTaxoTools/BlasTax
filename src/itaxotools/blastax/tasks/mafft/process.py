from datetime import datetime
from pathlib import Path
from time import perf_counter

from ..common.types import Results
from .types import AdjustDirection, AlignmentStrategy


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
) -> Results:
    from itaxotools import abort, get_feedback, progress_handler

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{strategy=}")
    print(f"{adjust_direction=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_paths)

    timestamp = datetime.now() if append_timestamp else None
    configuration: dict[str, str] = {}
    if append_configuration:
        configuration[strategy.key] = None
        if adjust_direction.option:
            configuration[adjust_direction.option] = None

    target_paths = [get_target_path(input_path, output_path, timestamp, configuration) for input_path in input_paths]

    if any((path.exists() for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (input_path, target_path) in enumerate(zip(input_paths, target_paths)):
        progress_handler(f"Processing file {i+1}/{total}: {input_path.name}", i, 0, total)
        single_work_dir = work_dir / input_path.name
        single_work_dir.mkdir()
        execute_single(
            work_dir=single_work_dir,
            input_path=input_path,
            target_path=target_path,
            strategy=strategy,
            adjust_direction=adjust_direction,
        )

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return Results(output_path, tf - ts)


def execute_single(
    work_dir: Path,
    input_path: Path,
    target_path: Path,
    strategy: AlignmentStrategy,
    adjust_direction: AdjustDirection,
):
    from itaxotools.mafftpy import MultipleSequenceAlignment

    a = MultipleSequenceAlignment(input_path)
    a.vars.set_strategy(strategy.key)
    a.vars.set_adjust_direction(adjust_direction.key)
    a.target = work_dir

    a.run()
    a.fetch(target_path)


def get_target_path(
    input_path: Path,
    output_dir: Path,
    timestamp: datetime | None,
    configuration: dict[str, str],
) -> Path:
    from itaxotools.blastax.core import get_output_filename

    return output_dir / get_output_filename(
        input_path=input_path,
        suffix=".fasta",
        description="aligned",
        timestamp=timestamp,
        **configuration,
    )
