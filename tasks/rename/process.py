from datetime import datetime
from pathlib import Path
from time import perf_counter

from ..common.types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    input_paths: list[Path],
    output_path: Path,
    sanitize: bool,
    rename_auto: bool,
    trim: bool,
    trim_position: str,
    trim_max_char: int,
    add: bool,
    add_position: str,
    add_text: str,
    append_timestamp: bool,
) -> Results:
    from core import fasta_name_modifier, get_fasta_renamed_filename
    from itaxotools import abort, get_feedback, progress_handler

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{sanitize=}")
    print(f"{rename_auto=}")
    print(f"{trim=}")
    print(f"{trim_position=}")
    print(f"{trim_max_char=}")
    print(f"{add=}")
    print(f"{add_position=}")
    print(f"{add_text=}")
    print(f"{append_timestamp=}")

    total = len(input_paths)

    timestamp = datetime.now() if append_timestamp else None

    target_paths = [output_path / get_fasta_renamed_filename(path, timestamp=timestamp) for path in input_paths]

    if any((path.exists() for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (path, target) in enumerate(zip(input_paths, target_paths)):
        progress_handler(f"{i}/{total}", i, 0, total)
        fasta_name_modifier(
            input_name=path,
            output_name=target,
            trim=trim,
            add=add,
            sanitize=sanitize,
            trimposition=trim_position,
            trimmaxchar=trim_max_char,
            renameauto=rename_auto,
            direc=add_position,
            addstring=add_text,
        )
    progress_handler(f"{total}/{total}", total, 0, total)

    tf = perf_counter()

    return Results(output_path, tf - ts)
