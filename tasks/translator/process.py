from pathlib import Path
from time import perf_counter

from ..common.types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import translator  # noqa


def execute(
    input_path: Path,
    output_path: Path,
    log_path: Path,
    nucleotide_path: Path,
    input_type: str,
    frame: str,
    code: int,
) -> Results:
    from translator import Options, translate

    print(f"{input_path=}")
    print(f"{output_path=}")
    print(f"{log_path=}")
    print(f"{nucleotide_path=}")
    print(f"{input_type=}")
    print(f"{frame=}")
    print(f"{code=}")

    ts = perf_counter()

    options = Options(
        input_path=input_path,
        output_path=output_path,
        log_path=log_path,
        nucleotide_path=nucleotide_path,
        input_type=input_type,
        frame=frame,
        code=code,
    )
    translate(options)

    tf = perf_counter()

    return Results(output_path, tf - ts)
