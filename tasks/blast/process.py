from pathlib import Path
from time import perf_counter

from ..common.types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    work_dir: Path,
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
    from core import run_blast
    from utils import remove_gaps

    print(f"{input_query_path=}")
    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{blast_outfmt=}")
    print(f"{blast_outfmt_options=}")
    print(f"{blast_extra_args=}")

    ts = perf_counter()

    blast_output_path = output_path / input_query_path.with_suffix(".out").name
    input_query_path_no_gaps = work_dir / input_query_path.with_stem(input_query_path.stem + "_no_gaps").name
    remove_gaps(input_query_path, input_query_path_no_gaps)

    if not run_blast(
        blast_binary=blast_method,
        query_path=input_query_path_no_gaps,
        database_path=input_database_path,
        output_path=blast_output_path,
        evalue=blast_evalue,
        num_threads=blast_num_threads,
        outfmt=f"{blast_outfmt} {blast_outfmt_options}",
        other=blast_extra_args,
        work_dir=work_dir,
    ):
        raise Exception("BLAST process failed! Please make sure the parameters are set correctly!")

    tf = perf_counter()

    return Results(output_path, tf - ts)
