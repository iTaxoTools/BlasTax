from datetime import datetime
from pathlib import Path
from time import perf_counter
from traceback import print_exc

from itaxotools.blastax.utils import make_str_blast_safe

from ..common.process import StagingArea
from ..common.types import BatchResults, Confirmation
from .types import TargetPaths


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
    blast_evalue: float,
    blast_num_threads: int,
    pident_threshold: float,
    retrieve_original: bool,
    deduplicate: bool,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler

    blast_method = "blastn"
    blast_outfmt = 6
    blast_outfmt_options = "qseqid sseqid sacc stitle pident qseq"

    print(f"{input_query_paths=}")
    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{pident_threshold=}")
    print(f"{retrieve_original=}")
    print(f"{deduplicate=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_query_paths)
    failed: list[Path] = []

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
        if deduplicate:
            museo_options["singles"] = None
        else:
            museo_options["all"] = None
        museo_options["pident"] = str(pident_threshold)

    target_paths_list = [
        get_target_paths(path, output_path, timestamp, blast_options, museo_options) for path in input_query_paths
    ]

    staging = StagingArea(work_dir)
    staging.add(db_paths=[input_database_path])
    if staging.requires_copy():
        if not get_feedback(Confirmation.StagingRequired):
            abort()

    if any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(Confirmation.OverwriteFiles):
            abort()

    ts = perf_counter()

    progress_handler("Staging database", 0, 0, 0)
    staging.stage(verbose=True)

    try:
        for i, (path, target) in enumerate(zip(input_query_paths, target_paths_list)):
            progress_handler(f"Processing file {i+1}/{total}: {path.name}", i, 0, total)
            try:
                execute_single(
                    work_dir=work_dir,
                    staging=staging,
                    input_query_path=path,
                    input_database_path=input_database_path,
                    blast_output_path=target.blast_output_path,
                    museo_output_path=target.museo_output_path,
                    blast_method=blast_method,
                    blast_evalue=blast_evalue,
                    blast_num_threads=blast_num_threads,
                    blast_outfmt=blast_outfmt,
                    blast_outfmt_options=blast_outfmt_options,
                    pident_threshold=pident_threshold,
                    retrieve_original=retrieve_original,
                    deduplicate=deduplicate,
                )
            except Exception as e:
                if total == 1:
                    raise e
                with open(target.error_log_path, "w") as f:
                    print_exc(file=f)
                failed.append(path)
    finally:
        staging.cleanup()

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_path, failed, tf - ts)


def execute_single(
    work_dir: Path,
    staging: StagingArea,
    input_query_path: Path,
    input_database_path: Path,
    blast_output_path: Path,
    museo_output_path: Path,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    blast_outfmt: int,
    blast_outfmt_options: str,
    pident_threshold: float,
    retrieve_original: bool,
    deduplicate: bool,
):
    from itaxotools.blastax.core import museoscript, run_blast
    from itaxotools.blastax.utils import fastq_to_fasta, is_fastq, remove_gaps

    if is_fastq(input_query_path):
        target_query_path = work_dir / input_query_path.with_suffix(".fasta").name
        fastq_to_fasta(input_query_path, target_query_path)
        input_query_path = target_query_path

    stem = make_str_blast_safe(input_query_path.stem) + "_no_gaps"
    input_query_path_no_gaps = work_dir / input_query_path.with_stem(stem).name
    remove_gaps(input_query_path, input_query_path_no_gaps)

    staging.add(output_paths=[blast_output_path])
    staging.stage()

    try:
        run_blast(
            blast_binary=blast_method,
            query_path=input_query_path_no_gaps,
            database_path=staging[input_database_path],
            output_path=staging[blast_output_path],
            evalue=blast_evalue,
            num_threads=blast_num_threads,
            outfmt=f"{blast_outfmt} {blast_outfmt_options}",
            other="",
        )

        museoscript(
            blast_path=staging[blast_output_path],
            output_path=museo_output_path,
            original_reads_path=input_query_path_no_gaps if retrieve_original else None,
            pident_threshold=pident_threshold,
            deduplicate=deduplicate,
        )
    finally:
        staging.unstage_outputs()


def get_target_paths(
    query_path: Path,
    output_path: Path,
    timestamp: datetime | None,
    blast_options: dict[str, str],
    museo_options: dict[str, str],
) -> TargetPaths:
    from itaxotools.blastax.core import (
        get_blast_filename,
        get_error_filename,
        get_museo_filename,
    )

    blast_output_path = output_path / get_blast_filename(query_path, outfmt=6, timestamp=timestamp, **blast_options)
    museo_output_path = output_path / get_museo_filename(
        query_path, timestamp=timestamp, **museo_options, **blast_options
    )
    error_log_path = output_path / get_error_filename(query_path, timestamp=timestamp)
    return TargetPaths(
        blast_output_path=blast_output_path,
        museo_output_path=museo_output_path,
        error_log_path=error_log_path,
    )
