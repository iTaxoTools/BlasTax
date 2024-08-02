from pathlib import Path
from time import perf_counter

from ..common.types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    input_query_path: Path,
    input_database_path: Path,
    output_path: Path,
    blast_evalue: float,
    blast_num_threads: int,
) -> Results:
    print(f"{input_query_path=}")
    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")

    ts = perf_counter()

    from time import sleep

    sleep(2)

    tf = perf_counter()

    return Results(output_path, tf - ts)
