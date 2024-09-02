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
    auto_increment: bool,
    trim: bool,
    trim_direction: str,
    trim_max_length: int,
    add: bool,
    add_direction: str,
    add_text: str,
    append_timestamp: bool,
) -> Results:
    from core import fasta_name_modifier, get_fasta_renamed_filename
    from itaxotools import abort, get_feedback, progress_handler

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{sanitize=}")
    print(f"{auto_increment=}")
    print(f"{trim=}")
    print(f"{trim_direction=}")
    print(f"{trim_max_length=}")
    print(f"{add=}")
    print(f"{add_direction=}")
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
            trimposition=trim_direction,
            trimmaxchar=trim_max_length,
            renameauto=auto_increment,
            direc=add_direction,
            addstring=add_text,
        )
    progress_handler(f"{total}/{total}", total, 0, total)

    tf = perf_counter()

    return Results(output_path, tf - ts)
