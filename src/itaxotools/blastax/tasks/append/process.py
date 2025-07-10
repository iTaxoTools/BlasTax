import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from time import perf_counter
from traceback import print_exc

from ..common.types import BatchResults, DoubleBatchResults
from .types import TargetPaths, TargetXPaths


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
    match_multiple: bool,
    match_pident: float,
    match_length: int,
    specified_identifier: str | None,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    print(f"{input_query_paths=}")
    print(f"{input_database_paths=}")
    print(f"{output_path=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{match_multiple=}")
    print(f"{match_pident=}")
    print(f"{match_length=}")
    print(f"{specified_identifier=}")
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
            match_multiple=match_multiple,
            match_pident=match_pident,
            match_length=match_length,
            specified_identifier=specified_identifier,
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
            match_multiple=match_multiple,
            match_pident=match_pident,
            match_length=match_length,
            specified_identifier=specified_identifier,
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
        match_multiple=match_multiple,
        match_pident=match_pident,
        match_length=match_length,
        specified_identifier=specified_identifier,
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
    match_multiple: bool,
    match_pident: float,
    match_length: int,
    specified_identifier: str | None,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    from core import get_append_filename

    from itaxotools import abort, get_feedback, progress_handler

    blast_outfmt = 6
    blast_outfmt_options = "length pident qseqid sseqid sseq qframe sframe"

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
        if match_multiple:
            match_options["multiple"] = None
            match_options["pident"] = match_pident
            match_options["length"] = match_length
        else:
            match_options["single"] = None

    appended_output_path = output_path / get_append_filename(input_query_path, timestamp=timestamp, **match_options)

    target_paths_list = [
        get_target_paths_x_database(input_query_path, input_database_path, output_path, timestamp, blast_options)
        for input_database_path in input_database_paths
    ]

    if appended_output_path.exists() or any(
        (path.exists() for target_paths in target_paths_list for path in target_paths)
    ):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    progress_handler(f"Copying query file: {input_query_path.name}", 0, 0, total)
    shutil.copyfile(input_query_path, appended_output_path)

    for i, (input_database_path, target) in enumerate(zip(input_database_paths, target_paths_list)):
        progress_handler(f"Processing query for database {i+1}/{total - 1}: {input_query_path.name}", i + 1, 0, total)
        try:
            execute_single_database_single_query(
                work_dir=work_dir,
                input_query_path=input_query_path,
                input_database_path=input_database_path,
                blast_output_path=target.blast_output_path,
                appended_output_path=appended_output_path,
                blast_method=blast_method,
                blast_outfmt=blast_outfmt,
                blast_outfmt_options=blast_outfmt_options,
                blast_evalue=blast_evalue,
                blast_num_threads=blast_num_threads,
                match_multiple=match_multiple,
                match_pident=match_pident,
                match_length=match_length,
                specified_identifier=specified_identifier,
                append_only=True,
            )
        except Exception:
            with open(target.error_log_path, "w") as f:
                print_exc(file=f)
            failed.append(input_database_path)

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
    match_multiple: bool,
    match_pident: float,
    match_length: int,
    specified_identifier: str | None,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler

    blast_outfmt = 6
    blast_outfmt_options = "length pident qseqid sseqid sseq qframe sframe"

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
        if match_multiple:
            match_options["multiple"] = None
            match_options["pident"] = match_pident
            match_options["length"] = match_length
        else:
            match_options["single"] = None

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

        for j, (input_query_path, target) in enumerate(zip(input_query_paths, target_paths_dict[input_database_path])):
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
                    appended_output_path=target.appended_output_path,
                    blast_method=blast_method,
                    blast_outfmt=blast_outfmt,
                    blast_outfmt_options=blast_outfmt_options,
                    blast_evalue=blast_evalue,
                    blast_num_threads=blast_num_threads,
                    match_multiple=match_multiple,
                    match_pident=match_pident,
                    match_length=match_length,
                    specified_identifier=specified_identifier,
                )
            except Exception as e:
                if total == 1:
                    raise e
                with open(target.error_log_path, "w") as f:
                    print_exc(file=f)
                failed[input_database_path].append(input_query_path)

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
    match_multiple: bool,
    match_pident: float,
    match_length: int,
    specified_identifier: str | None,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler

    blast_outfmt = 6
    blast_outfmt_options = "length pident qseqid sseqid sseq qframe sframe"

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
        if match_multiple:
            match_options["multiple"] = None
            match_options["pident"] = match_pident
            match_options["length"] = match_length
        else:
            match_options["single"] = None

    target_paths_list = [
        get_target_paths(path, output_path, timestamp, blast_options, match_options) for path in input_query_paths
    ]

    if any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (path, target) in enumerate(zip(input_query_paths, target_paths_list)):
        progress_handler(f"Processing file {i+1}/{total}: {path.name}", i, 0, total)
        try:
            execute_single_database_single_query(
                work_dir=work_dir,
                input_query_path=path,
                input_database_path=input_database_path,
                blast_output_path=target.blast_output_path,
                appended_output_path=target.appended_output_path,
                blast_method=blast_method,
                blast_outfmt=blast_outfmt,
                blast_outfmt_options=blast_outfmt_options,
                blast_evalue=blast_evalue,
                blast_num_threads=blast_num_threads,
                match_multiple=match_multiple,
                match_pident=match_pident,
                match_length=match_length,
                specified_identifier=specified_identifier,
            )
        except Exception as e:
            if total == 1:
                raise e
            with open(target.error_log_path, "w") as f:
                print_exc(file=f)
            failed.append(path)

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_path, failed, tf - ts)


def execute_single_database_single_query(
    work_dir: Path,
    input_query_path: Path,
    input_database_path: Path,
    blast_output_path: Path,
    appended_output_path: Path,
    blast_method: str,
    blast_outfmt: int,
    blast_outfmt_options: str,
    blast_evalue: float,
    blast_num_threads: int,
    match_multiple: bool,
    match_pident: float,
    match_length: int,
    specified_identifier: str | None,
    append_only: bool = False,
):
    from itaxotools.blastax.core import blast_parse, run_blast
    from itaxotools.blastax.utils import fastq_to_fasta, is_fastq, remove_gaps

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

    blast_parse(
        input_path=input_query_path,
        blast_result_path=blast_output_path,
        output_path=appended_output_path,
        database_name=input_database_path.stem,
        all_matches=match_multiple,
        pident_arg=match_pident,
        length_arg=match_length,
        user_spec_name=specified_identifier,
        append_only=append_only,
    )


def get_target_paths(
    query_path: Path,
    output_path: Path,
    timestamp: datetime | None,
    blast_options: dict[str, str],
    match_options: dict[str, str],
) -> TargetPaths:
    from itaxotools.blastax.core import get_append_filename, get_blast_filename, get_error_filename

    blast_output_path = output_path / get_blast_filename(query_path, outfmt=6, timestamp=timestamp, **blast_options)
    appended_output_path = output_path / get_append_filename(query_path, timestamp=timestamp, **match_options)
    error_log_path = output_path / get_error_filename(query_path, timestamp=timestamp)
    return TargetPaths(
        blast_output_path=blast_output_path,
        appended_output_path=appended_output_path,
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
