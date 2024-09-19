from pathlib import Path
from time import perf_counter

from ..common.types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    input_path: Path,
    output_path: Path,
    matching_regex: str,
    discard_duplicates: bool,
) -> Results:
    print(f"{input_path=}")
    print(f"{output_path=}")
    print(f"{matching_regex=}")
    print(f"{discard_duplicates=}")
    ts = perf_counter()

    tf = perf_counter()

    return Results(output_path, tf - ts)
