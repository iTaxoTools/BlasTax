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
    input_database_path: Path,
    input_nucleotides_path: Path,
    output_path: Path,
    blast_evalue: float,
    blast_num_threads: int,
    match_multiple: bool,
    match_pident: float,
    match_length: int,
    append_timestamp: bool,
    append_configuration: bool,
) -> Results:
    from itaxotools import abort, get_feedback, progress_handler

    blast_outfmt = 6
    blast_outfmt_options = "length pident qseqid sseqid sseq qframe sframe"

    print(f"{input_query_paths=}")
    print(f"{input_database_path=}")
    print(f"{input_nucleotides_path=}")
    print(f"{output_path=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{match_multiple=}")
    print(f"{match_pident=}")
    print(f"{match_length=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_query_paths)

    timestamp = datetime.now() if append_timestamp else None
    blast_options: dict[str, str] = {}
    match_options: dict[str, str] = {}
    if append_configuration:
        blast_options["blastx"] = None
        blast_options["evalue"] = blast_evalue
        parts = blast_outfmt_options.split(" ")
        blast_options["columns"] = "_".join(parts)
        match_options["blastx"] = None
        if match_multiple:
            match_options["multiple"] = None
        else:
            match_options["single"] = None
        match_options["pident"] = match_pident
        match_options["length"] = match_length

    target_paths_list = [
        get_target_paths(path, output_path, timestamp, blast_options, match_options) for path in input_query_paths
    ]

    if any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (path, target) in enumerate(zip(input_query_paths, target_paths_list)):
        progress_handler(f"{i}/{total}", i, 0, total)
        execute_single(
            work_dir=work_dir,
            input_query_path=path,
            input_database_path=input_database_path,
            input_nucleotides_path=input_nucleotides_path,
            blast_output_path=target.blast_output_path,
            appended_output_path=target.appended_output_path,
            blast_outfmt=blast_outfmt,
            blast_outfmt_options=blast_outfmt_options,
            blast_evalue=blast_evalue,
            blast_num_threads=blast_num_threads,
            match_multiple=match_multiple,
            match_pident=match_pident,
            match_length=match_length,
        )
    progress_handler(f"{total}/{total}", total, 0, total)

    tf = perf_counter()

    return Results(output_path, tf - ts)


def execute_single(
    work_dir: Path,
    input_query_path: Path,
    input_database_path: Path,
    input_nucleotides_path: Path,
    blast_output_path: Path,
    appended_output_path: Path,
    blast_outfmt: int,
    blast_outfmt_options: str,
    blast_evalue: float,
    blast_num_threads: int,
    match_multiple: bool,
    match_pident: float,
    match_length: int,
):
    from core import blastx_parse, run_blast
    from utils import fastq_to_fasta, is_fastq, remove_gaps

    if is_fastq(input_query_path):
        target_query_path = work_dir / input_query_path.with_suffix(".fasta").name
        fastq_to_fasta(input_query_path, target_query_path)
        input_query_path = target_query_path

    input_query_path_no_gaps = work_dir / input_query_path.with_stem(input_query_path.stem + "_no_gaps").name
    remove_gaps(input_query_path, input_query_path_no_gaps)

    run_blast(
        blast_binary="blastx",
        query_path=input_query_path_no_gaps,
        database_path=input_database_path,
        output_path=blast_output_path,
        evalue=blast_evalue,
        num_threads=blast_num_threads,
        outfmt=f"{blast_outfmt} {blast_outfmt_options}",
        other="",
    )

    blastx_parse(
        input_path=input_query_path,
        blast_result_path=blast_output_path,
        output_path=appended_output_path,
        extra_nucleotide_path=input_nucleotides_path,
        database_name=input_database_path.stem,
        all_matches=match_multiple,
        pident_arg=match_pident,
        length_arg=match_length,
    )


def get_target_paths(
    query_path: Path,
    output_path: Path,
    timestamp: datetime | None,
    blast_options: dict[str, str],
    match_options: dict[str, str],
) -> TargetPaths:
    from core import get_append_filename, get_blast_filename

    blast_output_path = output_path / get_blast_filename(query_path, outfmt=6, timestamp=timestamp, **blast_options)
    appended_output_path = output_path / get_append_filename(query_path, timestamp=timestamp, **match_options)
    return TargetPaths(
        blast_output_path=blast_output_path,
        appended_output_path=appended_output_path,
    )
