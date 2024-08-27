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
    query_path: Path,
    ingroup_database_path: Path,
    outgroup_database_path: Path,
    output_path: Path,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    append_timestamp: bool,
) -> Results:
    from core import decontaminate, get_decont_blast_filename, get_decont_sequences_filename, run_blast_decont
    from itaxotools import abort, get_feedback
    from utils import fastq_to_fasta, is_fastq, remove_gaps

    print(f"{query_path=}")
    print(f"{ingroup_database_path=}")
    print(f"{outgroup_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{append_timestamp=}")

    ts = perf_counter()

    if is_fastq(query_path):
        target_query_path = work_dir / query_path.with_suffix(".fasta").name
        fastq_to_fasta(query_path, target_query_path)
        query_path = target_query_path

    timestamp = datetime.now() if append_timestamp else None
    blasted_ingroup_path = output_path / get_decont_blast_filename(query_path, "ingroup", timestamp=timestamp)
    ingroup_sequences_path = output_path / get_decont_sequences_filename(query_path, "ingroup", timestamp=timestamp)
    blasted_outgroup_path = output_path / get_decont_blast_filename(query_path, "outgroup", timestamp=timestamp)
    outgroup_sequences_path = output_path / get_decont_sequences_filename(query_path, "outgroup", timestamp=timestamp)

    tc = perf_counter()

    if any(
        (
            path.exists()
            for path in [
                blasted_ingroup_path,
                ingroup_sequences_path,
                blasted_outgroup_path,
                outgroup_sequences_path,
            ]
        )
    ):
        if not get_feedback(None):
            abort()

    tx = perf_counter()

    input_query_path_no_gaps = work_dir / query_path.with_stem(query_path.stem + "_no_gaps").name
    remove_gaps(query_path, input_query_path_no_gaps)

    run_blast_decont(
        blast_binary=blast_method,
        query_path=query_path,
        database_path=ingroup_database_path,
        output_path=blasted_ingroup_path,
        evalue=blast_evalue,
        num_threads=blast_num_threads,
    )

    run_blast_decont(
        blast_binary=blast_method,
        query_path=query_path,
        database_path=ingroup_database_path,
        output_path=blasted_ingroup_path,
        evalue=blast_evalue,
        num_threads=blast_num_threads,
    )

    decontaminate(
        query_path=query_path,
        blasted_ingroup_path=blasted_ingroup_path,
        blasted_outgroup_path=blasted_outgroup_path,
        ingroup_sequences_path=ingroup_sequences_path,
        outgroup_sequences_path=outgroup_sequences_path,
    )

    tf = perf_counter()

    return Results(output_path, tf - tx + tc - ts)
