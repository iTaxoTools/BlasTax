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
    blast_evalue: float,
    blast_num_threads: int,
    pident_threshold: float,
    retrieve_original: bool,
) -> Results:
    from core import museoscript_original_reads, museoscript_parse, run_blast
    from utils import remove_gaps

    print(f"{input_query_path=}")
    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{pident_threshold=}")
    print(f"{retrieve_original=}")

    ts = perf_counter()

    blast_output_path = output_path / input_query_path.with_suffix(".out").name
    museo_output_path = output_path / input_query_path.with_stem(input_query_path.stem + "_museo").name
    input_query_path_no_gaps = work_dir / input_query_path.with_stem(input_query_path.stem + "_no_gaps").name
    remove_gaps(input_query_path, input_query_path_no_gaps)

    if not run_blast(
        blast_binary="blastn",
        query_path=input_query_path_no_gaps,
        database_path=input_database_path,
        output_path=blast_output_path,
        evalue=blast_evalue,
        num_threads=blast_num_threads,
        outfmt="6 qseqid sseqid sacc stitle pident qseq",
        other="",
    ):
        raise Exception("BLAST process failed! Please make sure the parameters are set correctly!")

    if retrieve_original:
        museoscript_original_reads(
            blast_path=blast_output_path,
            original_query_path=input_query_path_no_gaps,
            output_path=museo_output_path,
            pident_threshold=pident_threshold,
        )
    else:
        museoscript_parse(
            blast_path=blast_output_path,
            output_path=museo_output_path,
            pident_threshold=pident_threshold,
        )

    tf = perf_counter()

    return Results(output_path, tf - ts)
