from datetime import datetime
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
    append_timestamp: bool,
) -> Results:
    from core import get_blast_filename, run_blast
    from itaxotools import abort, get_feedback
    from utils import fastq_to_fasta, is_fastq, remove_gaps

    print(f"{input_query_path=}")
    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{blast_outfmt=}")
    print(f"{blast_outfmt_options=}")
    print(f"{blast_extra_args=}")
    print(f"{append_timestamp=}")

    ts = perf_counter()

    if is_fastq(input_query_path):
        target_query_path = work_dir / input_query_path.with_suffix(".fasta").name
        fastq_to_fasta(input_query_path, target_query_path)
        input_query_path = target_query_path

    timestamp = datetime.now() if append_timestamp else None
    blast_output_path = output_path / get_blast_filename(input_query_path, outfmt=blast_outfmt, timestamp=timestamp)

    tc = perf_counter()

    if blast_output_path.exists():
        if not get_feedback(blast_output_path):
            abort()

    tx = perf_counter()

    input_query_path_no_gaps = work_dir / input_query_path.with_stem(input_query_path.stem + "_no_gaps").name
    remove_gaps(input_query_path, input_query_path_no_gaps)

    run_blast(
        blast_binary=blast_method,
        query_path=input_query_path_no_gaps,
        database_path=input_database_path,
        output_path=blast_output_path,
        evalue=blast_evalue,
        num_threads=blast_num_threads,
        outfmt=f"{blast_outfmt} {blast_outfmt_options}",
        other=blast_extra_args,
    )

    tf = perf_counter()

    return Results(output_path, tf - tx + tc - ts)
