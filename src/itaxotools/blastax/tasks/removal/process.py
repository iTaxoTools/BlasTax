from pathlib import Path
from time import perf_counter

from ..common.types import Results
from .types import RemovalMode


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.codons  # noqa


def execute(
    input_paths: Path,
    output_path: Path,
    mode: RemovalMode,
    frame: str,
    code: int,
) -> Results:
    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{mode=}")
    print(f"{frame=}")
    print(f"{code=}")

    ts = perf_counter()

    match mode:
        case RemovalMode.discard_file:
            pass
        case RemovalMode.discard_sequence:
            pass
        case RemovalMode.trim_after_stop:
            pass

    tf = perf_counter()

    return Results(output_path, tf - ts)
