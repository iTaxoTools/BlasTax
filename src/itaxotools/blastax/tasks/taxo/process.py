import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from time import perf_counter
from traceback import print_exc

from itaxotools.blastax.utils import make_str_blast_safe

from ..common.process import stage_paths, unstage_paths
from ..common.types import BatchResults, DoubleBatchResults
from .types import TargetPaths, TargetXPaths

BLAST_OUTFMT_OPTIONS = "length pident qseqid sseqid staxids sscinames"


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.utils  # noqa


def execute(
    work_dir: Path,
    input_query_paths: list[Path],
    input_database_paths: list[Path],
    output_path: Path,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    blast_taxdb_path: Path,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    print(f"{input_query_paths=}")
    print(f"{input_database_paths=}")
    print(f"{output_path=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{blast_taxdb_path=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    if len(input_database_paths) == 1:
        input_database_path = input_database_paths[0]
        return execute_single_database_batch_queries(
            work_dir=work_dir,
            input_query_paths=input_query_paths,
            input_database_path=input_database_path,
            output_path=output_path,
            blast_method=blast_method,
            blast_evalue=blast_evalue,
            blast_num_threads=blast_num_threads,
            blast_taxdb_path=blast_taxdb_path,
            append_timestamp=append_timestamp,
            append_configuration=append_configuration,
        )

    if len(input_query_paths) == 1:
        input_query_path = input_query_paths[0]
        return execute_batch_databases_single_query(
            work_dir=work_dir,
            input_query_path=input_query_path,
            input_database_paths=input_database_paths,
            output_path=output_path,
            blast_method=blast_method,
            blast_evalue=blast_evalue,
            blast_num_threads=blast_num_threads,
            blast_taxdb_path=blast_taxdb_path,
            append_timestamp=append_timestamp,
            append_configuration=append_configuration,
        )

    return execute_batch_database_batch_queries(
        work_dir=work_dir,
        input_query_paths=input_query_paths,
        input_database_paths=input_database_paths,
        output_path=output_path,
        blast_method=blast_method,
        blast_evalue=blast_evalue,
        blast_num_threads=blast_num_threads,
        blast_taxdb_path=blast_taxdb_path,
        append_timestamp=append_timestamp,
        append_configuration=append_configuration,
    )


def execute_batch_databases_single_query(
    work_dir: Path,
    input_query_path: Path,
    input_database_paths: list[Path],
    output_path: Path,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    blast_taxdb_path: Path,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler
    from itaxotools.blastax.core import get_taxo_filename

    blast_outfmt = 6
    blast_outfmt_options = BLAST_OUTFMT_OPTIONS

    total = len(input_database_paths) + 1
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

    taxo_output_path = output_path / get_taxo_filename(input_query_path, timestamp=timestamp, **match_options)

    target_paths_list = [
        get_target_paths_x_database(input_query_path, input_database_path, output_path, timestamp, blast_options)
        for input_database_path in input_database_paths
    ]

    if taxo_output_path.exists() or any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    progress_handler(f"Copying query file: {input_query_path.name}", 0, 0, total)
    shutil.copyfile(input_query_path, taxo_output_path)

    for i, (input_database_path, target) in enumerate(zip(input_database_paths, target_paths_list)):
        progress_handler(f"Staging database {i+1}/{total - 1}", i + 1, 0, total)
        staged_paths = stage_paths(work_dir, [], [], [input_database_path])
        for k, v in staged_paths.items():
            print(f"Staged {repr(k)} as {repr(v)}")

        progress_handler(f"Processing query for database {i+1}/{total - 1}: {input_query_path.name}", i + 1, 0, total)
        try:
            execute_single_database_single_query(
                work_dir=work_dir,
                input_query_path=input_query_path,
                input_database_path=input_database_path,
                blast_output_path=target.blast_output_path,
                taxo_output_path=taxo_output_path,
                blast_method=blast_method,
                blast_outfmt=blast_outfmt,
                blast_outfmt_options=blast_outfmt_options,
                blast_evalue=blast_evalue,
                blast_num_threads=blast_num_threads,
                blast_taxdb_path=blast_taxdb_path,
                prestaged_paths=staged_paths,
            )
        except Exception:
            with open(target.error_log_path, "w") as f:
                print_exc(file=f)
            failed.append(input_database_path)
        finally:
            unstage_paths(work_dir, staged_paths)

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_path, failed, tf - ts)


def execute_batch_database_batch_queries(
    work_dir: Path,
    input_query_paths: list[Path],
    input_database_paths: list[Path],
    output_path: Path,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler

    blast_outfmt = 6
    blast_outfmt_options = BLAST_OUTFMT_OPTIONS

    total = len(input_query_paths) * len(input_database_paths)
    failed: dict[Path, BatchResults] = defaultdict(list)

    timestamp = datetime.now() if append_timestamp else None
    blast_options: dict[str, str] = {}
    match_options: dict[str, str] = {}
    if append_configuration:
        blast_options[blast_method] = None
        blast_options["evalue"] = blast_evalue
        parts = blast_outfmt_options.split(" ")
        blast_options["columns"] = "_".join(parts)
        match_options[blast_method] = None

    target_paths_dict = {
        input_database_path: [
            get_target_paths(
                input_query_path, output_path / input_database_path.name, timestamp, blast_options, match_options
            )
            for input_query_path in input_query_paths
        ]
        for input_database_path in input_database_paths
    }

    if any(
        (
            path.exists()
            for target_paths_list in target_paths_dict.values()
            for target_paths in target_paths_list
            for path in target_paths
        )
    ):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, input_database_path in enumerate(input_database_paths):
        database_output_path = output_path / input_database_path.name
        database_output_path.mkdir(exist_ok=True)

        progress_handler(f"Staging database {i+1}/{total - 1}", i + 1, 0, total)
        staged_paths = stage_paths(work_dir, [], [], [input_database_path])
        for k, v in staged_paths.items():
            print(f"Staged {repr(k)} as {repr(v)}")

        try:
            for j, (input_query_path, target) in enumerate(
                zip(input_query_paths, target_paths_dict[input_database_path])
            ):
                progress_handler(
                    f"Processing {repr(input_database_path.name)} for file: {input_query_path.name}",
                    len(input_query_paths) * i + j,
                    0,
                    total,
                )
                try:
                    execute_single_database_single_query(
                        work_dir=work_dir,
                        input_query_path=input_query_path,
                        input_database_path=input_database_path,
                        blast_output_path=target.blast_output_path,
                        taxo_output_path=target.taxo_output_path,
                        blast_method=blast_method,
                        blast_outfmt=blast_outfmt,
                        blast_outfmt_options=blast_outfmt_options,
                        blast_evalue=blast_evalue,
                        blast_num_threads=blast_num_threads,
                        prestaged_paths=staged_paths,
                    )
                except Exception as e:
                    if total == 1:
                        raise e
                    with open(target.error_log_path, "w") as f:
                        print_exc(file=f)
                    failed[input_database_path].append(input_query_path)
        finally:
            unstage_paths(work_dir, staged_paths)

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return DoubleBatchResults(output_path, failed, tf - ts)


def execute_single_database_batch_queries(
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

    if any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    progress_handler("Staging database", 0, 0, 0)
    staged_paths = stage_paths(work_dir, [], [], [input_database_path])
    for k, v in staged_paths.items():
        print(f"Staged {repr(k)} as {repr(v)}")

    try:
        for i, (path, target) in enumerate(zip(input_query_paths, target_paths_list)):
            progress_handler(f"Processing file {i+1}/{total}: {path.name}", i, 0, total)
            try:
                execute_single_database_single_query(
                    work_dir=work_dir,
                    input_query_path=path,
                    input_database_path=input_database_path,
                    blast_output_path=target.blast_output_path,
                    taxo_output_path=target.taxo_output_path,
                    blast_method=blast_method,
                    blast_outfmt=blast_outfmt,
                    blast_outfmt_options=blast_outfmt_options,
                    blast_evalue=blast_evalue,
                    blast_taxdb_path=blast_taxdb_path,
                    blast_num_threads=blast_num_threads,
                    prestaged_paths=staged_paths,
                )
            except Exception as e:
                if total == 1:
                    raise e
                with open(target.error_log_path, "w") as f:
                    print_exc(file=f)
                failed.append(path)
    finally:
        unstage_paths(work_dir, staged_paths)

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_path, failed, tf - ts)


def execute_single_database_single_query(
    work_dir: Path,
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
    prestaged_paths: dict[Path, Path] = None,
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

    staged_paths = stage_paths(work_dir, [], [blast_output_path], [input_database_path] if not prestaged_paths else [])
    for k, v in staged_paths.items():
        print(f"Staged {repr(k)} as {repr(v)}")

    if prestaged_paths:
        staged_paths |= prestaged_paths

    try:
        run_blast(
            blast_binary=blast_method,
            query_path=input_query_path_no_gaps,
            database_path=staged_paths[input_database_path],
            output_path=staged_paths[blast_output_path],
            evalue=blast_evalue,
            num_threads=blast_num_threads,
            outfmt=f"{blast_outfmt} {blast_outfmt_options}",
            other="",
            blastdb_path=blast_taxdb_path,
            debug=True,
        )
        assign_taxonomy(
            query_path=input_query_path,
            blast_path=staged_paths[blast_output_path],
            output_path=taxo_output_path,
        )

    finally:
        unstage_paths(work_dir, staged_paths, [blast_output_path], prestaged_paths is None)


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


def get_target_paths_x_database(
    query_path: Path,
    database_path: Path,
    output_path: Path,
    timestamp: datetime | None,
    blast_options: dict[str, str],
) -> TargetXPaths:
    from itaxotools.blastax.core import get_blast_filename, get_error_filename

    modified_query_path = query_path.with_stem(f"{query_path.stem}_x_{database_path.name}")
    blast_output_path = output_path / get_blast_filename(
        modified_query_path, outfmt=6, timestamp=timestamp, **blast_options
    )
    error_log_path = output_path / get_error_filename(modified_query_path, timestamp=timestamp)
    return TargetXPaths(
        blast_output_path=blast_output_path,
        error_log_path=error_log_path,
    )
