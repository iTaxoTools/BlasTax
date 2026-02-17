from datetime import datetime
from pathlib import Path
from time import perf_counter
from traceback import print_exc

from itaxotools.blastax.utils import make_str_blast_safe

from ..common.process import StagingArea
from ..common.types import BatchResults
from .types import TargetPaths

BLAST_OUTFMT_OPTIONS = "qseqid length pident staxids sscinames"


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
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    blast_taxdb_path: Path,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler

    blast_outfmt = 6
    blast_outfmt_options = BLAST_OUTFMT_OPTIONS

    print(f"{input_query_paths=}")
    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{blast_taxdb_path=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_query_paths)
    failed: list[Path] = []

    timestamp = datetime.now() if append_timestamp else None
    blast_options: dict[str, str] = {}
    match_options: dict[str, str] = {}
    if append_configuration:
        blast_options[blast_method] = None
        blast_options["evalue"] = blast_evalue
        parts = blast_outfmt_options.split(" ")
        blast_options["columns"] = "_".join(parts)
        match_options[blast_method] = None

    target_paths_list = [
        get_target_paths(path, output_path, timestamp, blast_options, match_options) for path in input_query_paths
    ]

    staging = StagingArea(work_dir)
    staging.add(db_paths=[input_database_path])
    if staging.requires_copy():
        if not get_feedback("STAGE"):
            abort()

    if any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(None):
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
                    taxo_output_path=target.taxo_output_path,
                    blast_method=blast_method,
                    blast_outfmt=blast_outfmt,
                    blast_outfmt_options=blast_outfmt_options,
                    blast_evalue=blast_evalue,
                    blast_num_threads=blast_num_threads,
                    blast_taxdb_path=blast_taxdb_path,
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
    taxo_output_path: Path,
    blast_method: str,
    blast_outfmt: int,
    blast_outfmt_options: str,
    blast_evalue: float,
    blast_num_threads: int,
    blast_taxdb_path: Path,
):
    from itaxotools.blastax.core import assign_taxonomy, run_blast
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
            blastdb_path=blast_taxdb_path,
            debug=True,
        )
        assign_taxonomy(
            query_path=input_query_path,
            blast_path=staging[blast_output_path],
            output_path=taxo_output_path,
        )

    finally:
        staging.unstage_outputs()


def get_target_paths(
    query_path: Path,
    output_path: Path,
    timestamp: datetime | None,
    blast_options: dict[str, str],
    match_options: dict[str, str],
) -> TargetPaths:
    from itaxotools.blastax.core import get_blast_filename, get_error_filename, get_taxo_filename

    blast_output_path = output_path / get_blast_filename(query_path, outfmt=6, timestamp=timestamp, **blast_options)
    taxo_output_path = output_path / get_taxo_filename(query_path, timestamp=timestamp, **match_options)
    error_log_path = output_path / get_error_filename(query_path, timestamp=timestamp)
    return TargetPaths(
        blast_output_path=blast_output_path,
        taxo_output_path=taxo_output_path,
        error_log_path=error_log_path,
    )
