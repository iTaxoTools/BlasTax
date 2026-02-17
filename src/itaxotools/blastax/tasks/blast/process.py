from datetime import datetime
from pathlib import Path
from time import perf_counter

from itaxotools.blastax.utils import make_str_blast_safe

from ..common.process import StagingArea
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
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    blast_outfmt: int,
    blast_outfmt_options: str,
    blast_extra_args: str,
    append_timestamp: bool,
    append_configuration: bool,
) -> Results:
    from itaxotools import abort, get_feedback, progress_handler
    from itaxotools.blastax.core import get_blast_filename, run_blast
    from itaxotools.blastax.utils import fastq_to_fasta, is_fastq, remove_gaps

    from ..common.types import BLAST_OUTFMT_SPECIFIERS_TABLE

    if blast_outfmt not in BLAST_OUTFMT_SPECIFIERS_TABLE.keys():
        blast_outfmt_options = ""
    blast_outfmt_options = blast_outfmt_options.strip()

    print(f"{input_query_path=}")
    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{blast_outfmt=}")
    print(f"{blast_outfmt_options=}")
    print(f"{blast_extra_args=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    timestamp = datetime.now() if append_timestamp else None
    options: dict[str, str] = {}
    if append_configuration:
        options[blast_method] = None
        options["evalue"] = blast_evalue
        if blast_outfmt_options:
            parts = blast_outfmt_options.split(" ")
            options["columns"] = "_".join(parts)
        if blast_extra_args:
            options["extra"] = None

    blast_output_path = output_path / get_blast_filename(
        input_query_path, outfmt=blast_outfmt, timestamp=timestamp, **options
    )

    if blast_output_path.exists():
        if not get_feedback(blast_output_path):
            abort()

    staging = StagingArea(work_dir)
    staging.add(output_paths=[blast_output_path], db_paths=[input_database_path])

    if staging.requires_copy():
        if not get_feedback("STAGE"):
            abort()

    ts = perf_counter()

    if is_fastq(input_query_path):
        target_query_path = work_dir / input_query_path.with_suffix(".fasta").name
        fastq_to_fasta(input_query_path, target_query_path)
        input_query_path = target_query_path

    stem = make_str_blast_safe(input_query_path.stem) + "_no_gaps"
    input_query_path_no_gaps = work_dir / input_query_path.with_stem(stem).name
    remove_gaps(input_query_path, input_query_path_no_gaps)

    progress_handler("Staging files", 0, 0, 0)
    staging.stage(verbose=True)

    with staging:
        progress_handler("Running BLAST+", 0, 0, 0)
        run_blast(
            blast_binary=blast_method,
            query_path=staging[input_query_path_no_gaps],
            database_path=staging[input_database_path],
            output_path=staging[blast_output_path],
            evalue=blast_evalue,
            num_threads=blast_num_threads,
            outfmt=f"{blast_outfmt} {blast_outfmt_options}",
            other=blast_extra_args,
            debug=True,
        )
        progress_handler("Done.", 1, 0, 1)

    tf = perf_counter()

    return Results(output_path, tf - ts)
