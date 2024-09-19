from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


def get_file_groups(
    directory: Path,
    matching_regex: str,
) -> list[Path]:
    regex = re.compile(matching_regex)
    groups = defaultdict(set)

    for path in directory.iterdir():
        if path.is_dir():
            continue
        match = regex.match(path.name)
        if match:
            group = match.group(1)
            groups[group].add(path.name)

    return groups


def merge_fasta_files(
    input_path: Path,
    output_path: Path,
    matching_regex: str,
    discard_duplicates: bool,
):
    if not input_path.exists():
        raise Exception("Input path does not exist.")
    if not input_path.is_dir():
        raise Exception("Input path is not a directory.")
    if not output_path.exists():
        raise Exception("Output path does not exist.")
    if not output_path.is_dir():
        raise Exception("Output path is not a directory.")

    get_file_groups(input_path, matching_regex)
