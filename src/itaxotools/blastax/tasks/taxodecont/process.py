from pathlib import Path
from time import perf_counter

from ..common.types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.utils  # noqa


def execute(
    work_dir: Path,
    input_query_paths: list[Path],
    input_database_path: Path,
    output_path: Path,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    threshold_pident: float | None,
    threshold_bitscore: float | None,
    threshold_length: float | None,
    append_timestamp: bool,
    append_configuration: bool,
) -> Results:
    from itaxotools import progress_handler

    print(f"{input_query_paths=}")
    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{threshold_pident=}")
    print(f"{threshold_bitscore=}")
    print(f"{threshold_length=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    ts = perf_counter()

    # TODO: implement taxonomic decontamination logic
    progress_handler("Not yet implemented", 0, 0, 0)

    tf = perf_counter()

    return Results(output_path, tf - ts)
