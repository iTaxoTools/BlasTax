from pathlib import Path

from .types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    batch_mode: bool,
    input_query_path: Path,
    input_database_path: Path,
    input_nucleotides_path: Path,
    input_query_list: list[Path],
    output_path: Path,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
) -> Results:
    print(f"{batch_mode=}")
    print(f"{input_query_path=}")
    print(f"{input_database_path=}")
    print(f"{input_nucleotides_path=}")
    print(f"{input_query_list=}")
    print(f"{output_path=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")

    return Results(None, 0.0)
