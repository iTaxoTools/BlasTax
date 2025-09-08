from datetime import datetime
from pathlib import Path
from time import perf_counter
from traceback import print_exc

from ..common.types import BatchResults
from .types import TargetPaths


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import cutadapt  # noqa


def execute(
    input_paths: list[Path],
    output_dir: Path,
    adapters_a: str,
    adapters_g: str,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler

    adapters_a_list = [line.strip() for line in adapters_a.splitlines()]
    adapters_g_list = [line.strip() for line in adapters_g.splitlines()]

    print(f"{input_paths=}")
    print(f"{output_dir=}")
    print(f"{adapters_a_list=}")
    print(f"{adapters_g_list=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_paths)
    failed: list[Path] = []

    timestamp = datetime.now() if append_timestamp else None
    options: dict[str, str] = {}
    if append_configuration:
        pass

    target_paths_list = [get_target_paths(path, output_dir, timestamp, options) for path in input_paths]

    if any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (path, target) in enumerate(zip(input_paths, target_paths_list)):
        progress_handler(f"Processing file {i+1}/{total}: {path.name}", i, 0, total)
        try:
            execute_single(
                input_path=path,
                output_path=target.output_path,
                adapters_a_list=adapters_a_list,
                adapters_g_list=adapters_g_list,
            )
        except Exception as e:
            if total == 1:
                raise e
            with open(target.error_log_path, "w") as f:
                print_exc(file=f)
            failed.append(path)

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_dir, failed, tf - ts)


def execute_single(
    input_path: Path,
    output_path: Path,
    adapters_a_list: list[str],
    adapters_g_list: list[str],
):
    from cutadapt.cli import main

    args = []

    for adapter in adapters_a_list:
        args.append("-a")
        args.append(adapter)

    for adapter in adapters_g_list:
        args.append("-g")
        args.append(adapter)

    args.append("-o")
    args.append(output_path.absolute())

    args.append(input_path.absolute())

    main(args)


def get_target_paths(
    input_path: Path,
    output_dir: Path,
    timestamp: datetime | None,
    configuration: dict[str, str],
) -> TargetPaths:
    from itaxotools.blastax.core import get_error_filename, get_output_filename

    suffix = "fastq" if input_path.suffix in [".fastq", ".fq"] else ".fasta"

    output_path = output_dir / get_output_filename(
        input_path=input_path,
        suffix=suffix,
        description="cutadapt",
        timestamp=timestamp,
        **configuration,
    )
    error_log_path = output_dir / get_error_filename(output_path)

    return TargetPaths(
        output_path=output_path,
        error_log_path=error_log_path,
    )
