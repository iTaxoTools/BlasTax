from pathlib import Path
from time import perf_counter

from ..common.types import Results
from .types import AmalgamationMethodTexts


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    input_paths: list[Path],
    output_path: Path,
    amalgamation_method: AmalgamationMethodTexts,
    append_timestamp: bool,
    append_configuration: bool,
) -> Results:
    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{amalgamation_method=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    ts = perf_counter()

    tf = perf_counter()

    return Results(output_path, tf - ts)
