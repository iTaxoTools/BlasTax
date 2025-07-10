from pathlib import Path
from time import perf_counter

from ..common.types import WarnResults
from .types import FormatGroup


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.fastmerge  # noqa


def execute(
    input_paths: list[Path],
    output_path: Path,
    format_group: FormatGroup,
    pattern_identifier: str,
    pattern_sequence: str,
    compress: bool,
) -> WarnResults:
    import gzip
    import warnings

    from itaxotools import progress_handler
    from itaxotools.blastax.fastmerge import fastmerge

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
    total = len(file_list)

    if compress:
        output = gzip.open(output_file + ".gz", mode="wt", errors="replace")
    else:
        output = open(output_file, mode="w", errors="replace")

    def progress_callback(file: str, index: int, total: int):
        path = Path(file)
        progress_handler(f"Processing file {index+1}/{total}: {path.name}", index, 0, total)

    with warnings.catch_warnings(record=True) as warns:
        fastmerge(
            file_list=file_list,
            file_types=file_types,
            seqid_pattern=pattern_identifier,
            sequence_pattern=pattern_sequence,
            output=output,
            progress_callback=progress_callback,
        )

    warn_messages = [warn.message for warn in warns]

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return WarnResults(output_path, warn_messages, tf - ts)
