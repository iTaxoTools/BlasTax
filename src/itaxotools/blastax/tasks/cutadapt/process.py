import io
import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter
from traceback import print_exc

from .types import CutAdaptResults, TargetPaths


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.blast  # noqa
    import cutadapt.cli  # noqa
    import yaml  # noqa

    monkeypatch()


def execute(
    input_paths: list[Path],
    output_dir: Path,
    adapters_a: str,
    adapters_g: str,
    cutadapt_action: str,
    cutadapt_error_rate: float,
    cutadapt_overlap: int,
    cutadapt_quality_trim_a: int,
    cutadapt_quality_trim_g: int,
    cutadapt_num_threads: int,
    cutadapt_extra_args: str,
    cutadapt_no_indels: bool,
    cutadapt_reverse_complement: bool,
    cutadapt_trim_poly_a: bool,
    write_reports: bool,
    append_timestamp: bool,
    append_configuration: bool,
) -> CutAdaptResults:
    from itaxotools import abort, get_feedback, progress_handler

    adapters_a_list = [line.strip() for line in adapters_a.splitlines()]
    adapters_g_list = [line.strip() for line in adapters_g.splitlines()]

    print(f"{input_paths=}")
    print(f"{output_dir=}")
    print(f"{adapters_a_list=}")
    print(f"{adapters_g_list=}")
    print(f"{cutadapt_action=}")
    print(f"{cutadapt_error_rate=}")
    print(f"{cutadapt_overlap=}")
    print(f"{cutadapt_quality_trim_a=}")
    print(f"{cutadapt_quality_trim_g=}")
    print(f"{cutadapt_num_threads=}")
    print(f"{cutadapt_extra_args=}")
    print(f"{cutadapt_no_indels=}")
    print(f"{cutadapt_reverse_complement=}")
    print(f"{cutadapt_trim_poly_a=}")
    print(f"{write_reports=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_paths)
    failed: list[Path] = []

    timestamp = datetime.now() if append_timestamp else None
    options: dict[str, str] = {}
    if append_configuration:
        options[cutadapt_action] = None
        options["e"] = f"{cutadapt_error_rate:.2f}"
        options["o"] = str(cutadapt_overlap)
        if cutadapt_quality_trim_a:
            options["q3"] = str(cutadapt_quality_trim_a)
        if cutadapt_quality_trim_g:
            options["q5"] = str(cutadapt_quality_trim_g)
        if cutadapt_no_indels:
            options["no_indels"] = None
        if cutadapt_reverse_complement:
            options["rev_comp"] = None
        if cutadapt_trim_poly_a:
            options["trim_poly_a"] = None
        if cutadapt_extra_args:
            options["extra_args"] = None

    target_paths_list = [get_target_paths(path, output_dir, write_reports, timestamp, options) for path in input_paths]

    if any((path.exists() for target_paths in target_paths_list for path in target_paths if path)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    sum_reads_total = 0
    sum_reads_cut = 0
    file_count = 0

    for i, (path, target) in enumerate(zip(input_paths, target_paths_list)):
        progress_handler(f"Processing file {i+1}/{total}: {path.name}", i, 0, total)
        try:
            reads_total, reads_cut = execute_single(
                input_path=path,
                output_path=target.output_path,
                report_path=target.report_path,
                adapters_a_list=adapters_a_list,
                adapters_g_list=adapters_g_list,
                cutadapt_action=cutadapt_action,
                cutadapt_error_rate=cutadapt_error_rate,
                cutadapt_overlap=cutadapt_overlap,
                cutadapt_quality_trim_a=cutadapt_quality_trim_a,
                cutadapt_quality_trim_g=cutadapt_quality_trim_g,
                cutadapt_num_threads=cutadapt_num_threads,
                cutadapt_extra_args=cutadapt_extra_args,
                cutadapt_no_indels=cutadapt_no_indels,
                cutadapt_reverse_complement=cutadapt_reverse_complement,
                cutadapt_trim_poly_a=cutadapt_trim_poly_a,
            )
            sum_reads_total += reads_total
            sum_reads_cut += reads_cut
            file_count += 1
        except Exception as e:
            if total == 1:
                raise e
            with open(target.error_log_path, "w") as f:
                print_exc(file=f)
            failed.append(path)

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return CutAdaptResults(output_dir, sum_reads_total, sum_reads_cut, failed, tf - ts)


def execute_single(
    input_path: Path,
    output_path: Path,
    report_path: Path | None,
    adapters_a_list: list[str],
    adapters_g_list: list[str],
    cutadapt_action: str,
    cutadapt_error_rate: float,
    cutadapt_overlap: int,
    cutadapt_quality_trim_a: int,
    cutadapt_quality_trim_g: int,
    cutadapt_num_threads: int,
    cutadapt_extra_args: str,
    cutadapt_no_indels: bool,
    cutadapt_reverse_complement: bool,
    cutadapt_trim_poly_a: bool,
) -> tuple[int, int]:
    import yaml

    from cutadapt.cli import main
    from itaxotools.blastax.blast import command_to_args

    args = []

    args.append("--action")
    args.append(cutadapt_action)

    args.append("--cores")
    args.append(str(cutadapt_num_threads))

    if cutadapt_error_rate > 1.0:
        args.append("--errors")
        args.append(str(cutadapt_error_rate))
    else:
        args.append("--error-rate")
        args.append(str(cutadapt_error_rate))

    args.append("--overlap")
    args.append(str(cutadapt_overlap))

    if cutadapt_quality_trim_a or cutadapt_quality_trim_g:
        args.append("--quality-cutoff")
        arg = str(cutadapt_quality_trim_a)
        if cutadapt_quality_trim_g:
            arg = str(cutadapt_quality_trim_g) + "," + arg
        args.append(arg)

    if cutadapt_no_indels:
        args.append("--no-indels")

    if cutadapt_reverse_complement:
        args.append("--revcomp")

    if cutadapt_trim_poly_a:
        args.append("--poly-a")

    for adapter in adapters_a_list:
        args.append("-a")
        args.append(adapter)

    for adapter in adapters_g_list:
        args.append("-g")
        args.append(adapter)

    args.extend(command_to_args(cutadapt_extra_args))

    args.append("-o")
    args.append(output_path.absolute())

    args.append(input_path.absolute())

    stats = main(args)

    if report_path:
        data: dict = stats.as_json()

        poly_a_tag = "poly_a_trimmed_read1"
        data[poly_a_tag] = [x.value for x in data[poly_a_tag]]

        with report_path.open("w") as file:
            yaml.safe_dump(data, file, sort_keys=False)

    return stats.n or 0, stats.with_adapters[0] or 0


def get_target_paths(
    input_path: Path,
    output_dir: Path,
    write_reports: bool,
    timestamp: datetime | None,
    configuration: dict[str, str],
) -> TargetPaths:
    from itaxotools.blastax.core import get_error_filename, get_output_filename

    suffix = ".fastq" if input_path.suffix in [".fastq", ".fq"] else ".fasta"

    output_path = output_dir / get_output_filename(
        input_path=input_path,
        suffix=suffix,
        description="cutadapt",
        timestamp=timestamp,
        **configuration,
    )
    report_path = None
    if write_reports:
        report_path = output_dir / get_output_filename(
            input_path=input_path,
            suffix=".log",
            description="statistics",
            timestamp=timestamp,
            **configuration,
        )
    error_log_path = output_dir / get_error_filename(output_path)

    return TargetPaths(
        output_path=output_path,
        report_path=report_path,
        error_log_path=error_log_path,
    )


def monkeypatch():
    import logging

    import cutadapt.cli

    # Patch stdin,required by cutadapt.runners.ParallelPipelineRunner
    # when running as PyInstaller executable

    if sys.stdin is None:

        class _DummyStdin(io.TextIOBase):
            def fileno(self):
                return -1

        sys.stdin = _DummyStdin()

    # Patch cutadapt parser to not call sys.exit

    _original_get_argument_parser = cutadapt.cli.get_argument_parser

    def patched_get_argument_parser(*args, **kwargs):
        parser = _original_get_argument_parser(*args, **kwargs)

        def _error(message):
            raise Exception(f"Argument error: {message}")

        parser.error = _error

        return parser

    cutadapt.cli.get_argument_parser = patched_get_argument_parser

    # Raise exception on log right before sys.exit is called

    class RaiseOnErrorHandler(logging.Handler):
        def emit(self, record):
            if record.levelno >= logging.ERROR:
                raise Exception(f"{record.getMessage()}")

    cutadapt.cli.logger.addHandler(RaiseOnErrorHandler())
