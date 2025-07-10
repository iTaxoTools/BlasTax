from pathlib import Path
from time import perf_counter

from ..common.types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import merge  # noqa


def execute(
    input_path: Path,
    output_path: Path,
    matching_regex: str,
    discard_duplicates: bool,
) -> Results:
    import re

    from merge import get_file_groups, merge_fasta_files

    from itaxotools import progress_handler

    print(f"{input_path=}")
    print(f"{output_path=}")
    print(f"{matching_regex=}")
    print(f"{discard_duplicates=}")
    ts = perf_counter()

    try:
        re.compile(matching_regex)
    except re.error:
        raise Exception("Invalid regular expression!")

    if matching_regex.count("(") != 1:
        raise Exception("Provided regex must contain exactly one capturing group!")

    groups = get_file_groups(input_path, matching_regex)

    if not groups:
        raise Exception("No matches could be found for selected rule!")

    total = len(groups)
    for i, (group, filenames) in enumerate(groups.items()):
        progress_handler(f"{i}/{total}", i, 0, total)
        input_paths = [input_path / filename for filename in filenames]
        merge_fasta_files(input_paths, output_path / f"{group}_merged.fasta", discard_duplicates)
    progress_handler(f"{total}/{total}", total, 0, total)

    tf = perf_counter()

    return Results(output_path, tf - ts)
