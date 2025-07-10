from datetime import datetime
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
    input_query_path: Path,
    input_database_path: Path,
    output_path: Path,
    blast_evalue: float,
    blast_num_threads: int,
    pident_threshold: float,
    retrieve_original: bool,
    append_timestamp: bool,
    append_configuration: bool,
) -> Results:
    from itaxotools import abort, get_feedback
    from itaxotools.blastax.core import (
        get_blast_filename,
        get_museo_filename,
        museoscript_original_reads,
        museoscript_parse,
        run_blast,
    )
    from itaxotools.blastax.utils import fastq_to_fasta, is_fastq, remove_gaps

    blast_method = "blastn"
    blast_outfmt = 6
    blast_outfmt_options = "qseqid sseqid sacc stitle pident qseq"

    print(f"{input_query_path=}")
    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{pident_threshold=}")
    print(f"{retrieve_original=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    timestamp = datetime.now() if append_timestamp else None
    blast_options: dict[str, str] = {}
    museo_options: dict[str, str] = {}
    if append_configuration:
        blast_options[blast_method] = None
        blast_options["evalue"] = blast_evalue
        parts = blast_outfmt_options.split(" ")
        blast_options["columns"] = "_".join(parts)
        if retrieve_original:
            museo_options["originals"] = None
        else:
            museo_options["matches"] = None
        museo_options["pident"] = str(pident_threshold)

    blast_output_path = output_path / get_blast_filename(
        input_query_path, outfmt=6, timestamp=timestamp, **blast_options
    )
    museo_output_path = output_path / get_museo_filename(
        input_query_path, timestamp=timestamp, **museo_options, **blast_options
    )

    if blast_output_path.exists() or museo_output_path.exists():
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    if is_fastq(input_query_path):
        target_query_path = work_dir / input_query_path.with_suffix(".fasta").name
        fastq_to_fasta(input_query_path, target_query_path)
        input_query_path = target_query_path

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
        other="",
    )

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
