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
    batch_mode: bool,
    input_query_path: Path,
    input_database_path: Path,
    input_nucleotides_path: Path,
    input_query_list: list[Path],
    output_path: Path,
    blast_evalue: float,
    blast_num_threads: int,
    append_timestamp: bool,
) -> Results:
    from core import get_append_filename, get_blast_filename
    from itaxotools import abort, get_feedback, progress_handler

    print(f"{batch_mode=}")
    print(f"{input_query_path=}")
    print(f"{input_database_path=}")
    print(f"{input_nucleotides_path=}")
    print(f"{input_query_list=}")
    print(f"{output_path=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{append_timestamp=}")

    ts = perf_counter()

    if batch_mode:
        input_query_paths = input_query_list
    else:
        input_query_paths = [input_query_path]
    total = len(input_query_paths)

    timestamp = datetime.now() if append_timestamp else None

    tc = perf_counter()

    if any(
        (
            (output_path / get_blast_filename(path, outfmt=6, timestamp=timestamp)).exists()
            or (output_path / get_append_filename(path, timestamp=timestamp)).exists()
            for path in input_query_paths
        )
    ):
        if not get_feedback(None):
            abort()

    tx = perf_counter()

    for i, path in enumerate(input_query_paths):
        progress_handler(f"{i}/{total}", i, 0, total)
        execute_single(
            work_dir=work_dir,
            input_query_path=path,
            input_database_path=input_database_path,
            input_nucleotides_path=input_nucleotides_path,
            output_path=output_path,
            blast_evalue=blast_evalue,
            blast_num_threads=blast_num_threads,
            timestamp=timestamp,
        )
    progress_handler(f"{total}/{total}", total, 0, total)

    tf = perf_counter()

    return Results(output_path, tf - tx + tc - ts)


def execute_single(
    work_dir: Path,
    input_query_path: Path,
    input_database_path: Path,
    input_nucleotides_path: Path,
    output_path: Path,
    blast_evalue: float,
    blast_num_threads: int,
    timestamp: datetime | None,
):
    from core import blastx_parse, get_append_filename, get_blast_filename, run_blast
    from utils import fastq_to_fasta, is_fastq, remove_gaps

    if is_fastq(input_query_path):
        target_query_path = work_dir / input_query_path.with_suffix(".fasta").name
        fastq_to_fasta(input_query_path, target_query_path)
        input_query_path = target_query_path

    blast_output_path = output_path / get_blast_filename(input_query_path, outfmt=6, timestamp=timestamp)
    appended_output_path = output_path / get_append_filename(input_query_path, timestamp=timestamp)
    input_query_path_no_gaps = work_dir / input_query_path.with_stem(input_query_path.stem + "_no_gaps").name
    remove_gaps(input_query_path, input_query_path_no_gaps)

    run_blast(
        blast_binary="blastx",
        query_path=input_query_path_no_gaps,
        database_path=input_database_path,
        output_path=blast_output_path,
        evalue=blast_evalue,
        num_threads=blast_num_threads,
        outfmt="6 length pident qseqid sseqid sseq qframe sframe",
        other="",
    )

    blastx_parse(
        input_path=input_query_path,
        blast_result_path=blast_output_path,
        output_path=appended_output_path,
        extra_nucleotide_path=input_nucleotides_path,
        database_name=input_database_path.stem,
    )
