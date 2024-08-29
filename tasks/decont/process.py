from datetime import datetime
from pathlib import Path
from time import perf_counter

from ..common.types import Results
from .types import TargetPaths


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    work_dir: Path,
    input_query_paths: list[Path],
    ingroup_database_path: Path,
    outgroup_database_path: Path,
    output_path: Path,
    decont_column: int,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    append_timestamp: bool,
) -> Results:
    from itaxotools import abort, get_feedback, progress_handler

    print(f"{input_query_paths=}")
    print(f"{ingroup_database_path=}")
    print(f"{outgroup_database_path=}")
    print(f"{output_path=}")
    print(f"{decont_column=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{append_timestamp=}")

    total = len(input_query_paths)

    timestamp = datetime.now() if append_timestamp else None

    target_paths_list = [get_target_paths(path, output_path, timestamp) for path in input_query_paths]

    if any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (path, target) in enumerate(zip(input_query_paths, target_paths_list)):
        progress_handler(f"{i}/{total}", i, 0, total)
        execute_single(
            work_dir=work_dir,
            input_query_path=path,
            ingroup_database_path=ingroup_database_path,
            outgroup_database_path=outgroup_database_path,
            blasted_ingroup_path=target.blasted_ingroup_path,
            ingroup_sequences_path=target.ingroup_sequences_path,
            blasted_outgroup_path=target.blasted_outgroup_path,
            outgroup_sequences_path=target.outgroup_sequences_path,
            decont_column=decont_column,
            blast_method=blast_method,
            blast_evalue=blast_evalue,
            blast_num_threads=blast_num_threads,
        )
    progress_handler(f"{total}/{total}", total, 0, total)

    tf = perf_counter()

    return Results(output_path, tf - ts)


def execute_single(
    work_dir: Path,
    input_query_path: Path,
    ingroup_database_path: Path,
    outgroup_database_path: Path,
    blasted_ingroup_path: Path,
    ingroup_sequences_path: Path,
    blasted_outgroup_path: Path,
    outgroup_sequences_path: Path,
    decont_column: int,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
):
    from core import decontaminate, run_blast_decont
    from utils import fastq_to_fasta, is_fastq, remove_gaps

    if is_fastq(input_query_path):
        target_query_path = work_dir / input_query_path.with_suffix(".fasta").name
        fastq_to_fasta(input_query_path, target_query_path)
        input_query_path = target_query_path

    input_query_path_no_gaps = work_dir / input_query_path.with_stem(input_query_path.stem + "_no_gaps").name
    remove_gaps(input_query_path, input_query_path_no_gaps)

    run_blast_decont(
        blast_binary=blast_method,
        query_path=input_query_path,
        database_path=ingroup_database_path,
        output_path=blasted_ingroup_path,
        evalue=blast_evalue,
        num_threads=blast_num_threads,
    )

    run_blast_decont(
        blast_binary=blast_method,
        query_path=input_query_path,
        database_path=outgroup_database_path,
        output_path=blasted_outgroup_path,
        evalue=blast_evalue,
        num_threads=blast_num_threads,
    )

    decontaminate(
        query_path=input_query_path,
        blasted_ingroup_path=blasted_ingroup_path,
        blasted_outgroup_path=blasted_outgroup_path,
        ingroup_sequences_path=ingroup_sequences_path,
        outgroup_sequences_path=outgroup_sequences_path,
        column=decont_column,
    )


def get_target_paths(
    query_path: Path,
    output_path: Path,
    timestamp: datetime | None,
) -> TargetPaths:
    from core import get_decont_blast_filename, get_decont_sequences_filename

    blasted_ingroup_path = output_path / get_decont_blast_filename(query_path, "ingroup", timestamp=timestamp)
    ingroup_sequences_path = output_path / get_decont_sequences_filename(
        query_path, "decontaminated", timestamp=timestamp
    )
    blasted_outgroup_path = output_path / get_decont_blast_filename(query_path, "outgroup", timestamp=timestamp)
    outgroup_sequences_path = output_path / get_decont_sequences_filename(
        query_path, "contaminants", timestamp=timestamp
    )
    return TargetPaths(
        blasted_ingroup_path=blasted_ingroup_path,
        ingroup_sequences_path=ingroup_sequences_path,
        blasted_outgroup_path=blasted_outgroup_path,
        outgroup_sequences_path=outgroup_sequences_path,
    )
