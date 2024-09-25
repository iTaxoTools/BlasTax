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
    output_format: str,
    max_size: int,
    split_n: int,
    pattern_identifier: str,
    pattern_sequence: str,
    compress: bool,
) -> Results:
    import warnings

    from fastsplit import fastsplit

    print(f"{input_path=}")
    print(f"{output_path=}")
    print(f"{filename_template=}")
    print(f"{output_format=}")
    print(f"{max_size=}")
    print(f"{split_n=}")
    print(f"{pattern_identifier=}")
    print(f"{pattern_sequence=}")
    print(f"{compress=}")

    ts = perf_counter()

    with warnings.catch_warnings(record=True) as warns:
        template = output_path / filename_template
        fastsplit(
            file_format=output_format,
            split_n=split_n,
            maxsize=max_size,
            seqid_pattern=pattern_identifier,
            sequence_pattern=pattern_sequence,
            infile_path=str(input_path.resolve()),
            compressed=compress,
            outfile_template=str(template.resolve()),
        )
    for w in warns:
        print("Warning", str(w.message))

    tf = perf_counter()

    return Results(output_path, tf - ts)
