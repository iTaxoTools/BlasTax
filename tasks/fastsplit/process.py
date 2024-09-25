from pathlib import Path
from time import perf_counter

from ..common.types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import fastsplit  # noqa


def execute(
    input_path: Path,
    output_path: Path,
    filename_template: str,
    max_size: int,
    split_n: int,
    pattern_identifier: str,
    pattern_sequence: str,
    compress: bool,
) -> Results:
    print(f"{input_path=}")
    print(f"{output_path=}")
    print(f"{filename_template=}")
    print(f"{max_size=}")
    print(f"{split_n=}")
    print(f"{pattern_identifier=}")
    print(f"{pattern_sequence=}")
    print(f"{compress=}")

    ts = perf_counter()

    tf = perf_counter()

    return Results(output_path, tf - ts)
