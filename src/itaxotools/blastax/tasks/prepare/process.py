from datetime import datetime
from pathlib import Path
from time import perf_counter
from traceback import print_exc

from ..common.types import BatchResults


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.utils  # noqa


def execute(
    input_paths: list[Path],
    output_path: Path,
    sanitize: bool,
    preserve_separators: bool,
    auto_increment: bool,
    trim: bool,
    trim_direction: str,
    trim_max_length: int,
    add: bool,
    add_direction: str,
    add_text: str,
    replace: bool,
    replace_source: str,
    replace_target: str,
    fixseqspaces: bool,
    fixseqasterisks: bool,
    fixaliseparator: bool,
    append_timestamp: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler
    from itaxotools.blastax.core import fasta_name_modifier, get_error_filename, get_fasta_prepared_filename

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{sanitize=}")
    print(f"{preserve_separators=}")
    print(f"{auto_increment=}")
    print(f"{trim=}")
    print(f"{trim_direction=}")
    print(f"{trim_max_length=}")
    print(f"{add=}")
    print(f"{add_direction=}")
    print(f"{add_text=}")
    print(f"{replace=}")
    print(f"{replace_source=}")
    print(f"{replace_target=}")
    print(f"{fixseqspaces=}")
    print(f"{fixseqasterisks=}")
    print(f"{fixaliseparator=}")
    print(f"{append_timestamp=}")

    total = len(input_paths)
    failed: list[Path] = []

    timestamp = datetime.now() if append_timestamp else None

    target_paths = [output_path / get_fasta_prepared_filename(path, timestamp=timestamp) for path in input_paths]

    if any((path.exists() for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (path, target) in enumerate(zip(input_paths, target_paths)):
        progress_handler(f"Processing file {i+1}/{total}: {path.name}", i, 0, total)
        try:
            fasta_name_modifier(
                input_name=path,
                output_name=target,
                trim=trim,
                add=add,
                replace=replace,
                sanitize=sanitize,
                preserve_separators=preserve_separators,
                trimposition=trim_direction,
                trimmaxchar=trim_max_length,
                renameauto=auto_increment,
                direc=add_direction,
                addstring=add_text,
                findstring=replace_source,
                replacestring=replace_target,
                fixseqspaces=fixseqspaces,
                fixseqasterisks=fixseqasterisks,
                fixaliseparator=fixaliseparator,
            )
        except Exception as e:
            if total == 1:
                raise e
            error_log_path = output_path / get_error_filename(path)
            with open(error_log_path, "w") as f:
                print_exc(file=f)
            failed.append(path)

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_path, failed, tf - ts)
