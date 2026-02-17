from datetime import datetime
from pathlib import Path
from time import perf_counter
from traceback import print_exc

from itaxotools.blastax.utils import make_str_blast_safe

from ..common.process import StagingArea
from ..common.types import BatchResults
from .types import TargetPaths


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.utils  # noqa


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
    append_configuration: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler

    from .types import DecontVariable

    blast_outfmt_options = "qseqid sseqid pident bitscore length"

    print(f"{input_query_paths=}")
    print(f"{ingroup_database_path=}")
    print(f"{outgroup_database_path=}")
    print(f"{output_path=}")
    print(f"{decont_column=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_query_paths)
    failed: list[Path] = []

    timestamp = datetime.now() if append_timestamp else None

    blast_options: dict[str, str] = {}
    decont_options: dict[str, str] = {}
    if append_configuration:
        blast_options[blast_method] = None
        blast_options["evalue"] = blast_evalue
        parts = blast_outfmt_options.split(" ")
        blast_options["columns"] = "_".join(parts)
        decont_options["variable"] = DecontVariable.from_column(decont_column).variable

    target_paths_list = [
        get_target_paths(path, output_path, timestamp, blast_options, decont_options) for path in input_query_paths
    ]

    staging = StagingArea(work_dir)
    staging.add(db_paths=[ingroup_database_path, outgroup_database_path])
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
    from itaxotools.blastax.core import decontaminate, run_blast_decont
    from itaxotools.blastax.utils import fastq_to_fasta, is_fastq, remove_gaps

    if is_fastq(input_query_path):
        target_query_path = work_dir / input_query_path.with_suffix(".fasta").name
        fastq_to_fasta(input_query_path, target_query_path)
        input_query_path = target_query_path

    stem = make_str_blast_safe(input_query_path.stem) + "_no_gaps"
    input_query_path_no_gaps = work_dir / input_query_path.with_stem(stem).name
    remove_gaps(input_query_path, input_query_path_no_gaps)

    staging.add(output_paths=[blasted_ingroup_path, blasted_outgroup_path])
    staging.stage()

    try:
        run_blast_decont(
            blast_binary=blast_method,
            query_path=input_query_path_no_gaps,
            database_path=staging[ingroup_database_path],
            output_path=staging[blasted_ingroup_path],
            evalue=blast_evalue,
            num_threads=blast_num_threads,
        )

        run_blast_decont(
            blast_binary=blast_method,
            query_path=input_query_path_no_gaps,
            database_path=staging[outgroup_database_path],
            output_path=staging[blasted_outgroup_path],
            evalue=blast_evalue,
            num_threads=blast_num_threads,
        )

        decontaminate(
            query_path=input_query_path,
            blasted_ingroup_path=staging[blasted_ingroup_path],
            blasted_outgroup_path=staging[blasted_outgroup_path],
            ingroup_sequences_path=ingroup_sequences_path,
            outgroup_sequences_path=outgroup_sequences_path,
            column=decont_column,
        )
    finally:
        staging.unstage_outputs()


def get_target_paths(
    query_path: Path,
    output_path: Path,
    timestamp: datetime | None,
    blast_options: dict[str, str],
    decont_options: dict[str, str],
) -> TargetPaths:
    from itaxotools.blastax.core import get_decont_blast_filename, get_decont_sequences_filename, get_error_filename

    blasted_ingroup_path = output_path / get_decont_blast_filename(
        query_path,
        "ingroup",
        timestamp=timestamp,
        **blast_options,
    )
    ingroup_sequences_path = output_path / get_decont_sequences_filename(
        query_path,
        "decontaminated",
        timestamp=timestamp,
        **decont_options,
        **blast_options,
    )
    blasted_outgroup_path = output_path / get_decont_blast_filename(
        query_path,
        "outgroup",
        timestamp=timestamp,
        **blast_options,
    )
    outgroup_sequences_path = output_path / get_decont_sequences_filename(
        query_path,
        "contaminants",
        timestamp=timestamp,
        **decont_options,
        **blast_options,
    )
    error_log_path = output_path / get_error_filename(query_path, timestamp=timestamp)
    return TargetPaths(
        blasted_ingroup_path=blasted_ingroup_path,
        ingroup_sequences_path=ingroup_sequences_path,
        blasted_outgroup_path=blasted_outgroup_path,
        outgroup_sequences_path=outgroup_sequences_path,
        error_log_path=error_log_path,
    )
