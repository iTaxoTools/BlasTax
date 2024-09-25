from pathlib import Path
from time import perf_counter

from ..common.types import Results
from .types import FormatGroup


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import fastmerge  # noqa


def execute(
    input_paths: list[Path],
    output_path: Path,
    format_group: FormatGroup,
    pattern_identifier: str,
    pattern_sequence: str,
    compress: bool,
) -> Results:
    import gzip
    import warnings

    from fastmerge import fastmerge

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{format_group=}")
    print(f"{pattern_identifier=}")
    print(f"{pattern_sequence=}")
    print(f"{compress=}")

    ts = perf_counter()

    file_list = [str(path.resolve()) for path in input_paths]
    file_types = format_group.types
    output_file = str(output_path.resolve())

    if compress:
        output = gzip.open(output_file + ".gz", mode="wt", errors="replace")
    else:
        output = open(output_file, mode="w", errors="replace")

    with warnings.catch_warnings(record=True) as warns:
        fastmerge(file_list, file_types, pattern_identifier, pattern_sequence, output)
    for w in warns:
        print("Warning", str(w.message))

    tf = perf_counter()

    return Results(output_path, tf - ts)
