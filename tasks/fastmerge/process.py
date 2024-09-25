from pathlib import Path
from time import perf_counter

from ..common.types import Results
from .types import FormatGroup


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import fastmerge  # noqa


def execute(
    input_path: Path,
    output_path: Path,
    format_group: FormatGroup,
    pattern_identifier: str,
    pattern_sequence: str,
) -> Results:
    print(f"{input_path=}")
    print(f"{output_path=}")
    print(f"{format_group=}")
    print(f"{pattern_identifier=}")
    print(f"{pattern_sequence=}")
    ts = perf_counter()

    tf = perf_counter()

    return Results(output_path, tf - ts)
