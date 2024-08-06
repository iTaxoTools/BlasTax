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
) -> Results:
    print(f"{batch_mode=}")
    print(f"{input_query_path=}")
    print(f"{input_database_path=}")
    print(f"{input_nucleotides_path=}")
    print(f"{input_query_list=}")
    print(f"{output_path=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")

    ts = perf_counter()

    if batch_mode:
        input_query_paths = input_query_list
    else:
        input_query_paths = [input_query_path]

    for path in input_query_paths:
        execute_single(
            work_dir=work_dir,
            input_query_path=path,
            input_database_path=input_database_path,
            input_nucleotides_path=input_nucleotides_path,
            output_path=output_path,
            blast_evalue=blast_evalue,
            blast_num_threads=blast_num_threads,
        )

    tf = perf_counter()

    return Results(output_path, tf - ts)


def execute_single(
    work_dir: Path,
    input_query_path: Path,
    input_database_path: Path,
    input_nucleotides_path: Path,
    output_path: Path,
    blast_evalue: float,
    blast_num_threads: int,
):
    from core import blastx_parse, run_blast
    from utils import remove_gaps

    print(input_database_path.name)

    blast_output_path = output_path / input_query_path.with_suffix(".out").name
    appended_output_path = output_path / input_query_path.with_stem(input_query_path.stem + "_with_blast_matches").name
    input_query_path_no_gaps = work_dir / input_query_path.with_stem(input_query_path.stem + "_no_gaps").name
    remove_gaps(input_query_path, input_query_path_no_gaps)

    if not run_blast(
        blast_binary="blastx",
        query_path=input_query_path_no_gaps,
        database_path=input_database_path,
        output_path=blast_output_path,
        evalue=blast_evalue,
        num_threads=blast_num_threads,
        outfmt="6 length pident qseqid sseqid sseq qframe sframe",
        other="",
    ):
        raise Exception(
            f"BLAST process failed for {input_database_path.name}! "
            "Please make sure the parameters are set correctly!"
        )

    blastx_parse(
        input_path=input_query_path,
        blast_result_path=blast_output_path,
        output_path=appended_output_path,
        extra_nucleotide_path=input_nucleotides_path,
        database_name=input_database_path.stem,
    )
