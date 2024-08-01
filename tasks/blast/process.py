from pathlib import Path

from .types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    input_query_path: Path,
    input_database_path: Path,
    output_path: Path,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    blast_outfmt: int,
    blast_outfmt_options: str,
    blast_extra_args: str,
) -> Results:
    print(f"{input_query_path=}")
    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{blast_outfmt=}")
    print(f"{blast_outfmt_options=}")
    print(f"{blast_extra_args=}")

    return Results(None, 0.0)
