from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from itaxotools.taxi2.sequences import SequenceHandler


def get_file_groups(
    directory: Path,
    matching_regex: str,
) -> list[str]:
    regex = re.compile(matching_regex)
    groups = defaultdict(set)

    for path in directory.iterdir():
        if path.is_dir():
            continue
        filename = path.name
        match = regex.match(filename)
        if match:
            group = match.group(1)
            groups[group].add(filename)

    return groups


def merge_fasta_files(
    input_paths: list[Path],
    output_path: Path,
    discard_duplicates: bool,
):
    identifiers = set()

    with SequenceHandler.Fasta(output_path, "w", line_width=0) as output_file:
        for input_path in input_paths:
            with SequenceHandler.Fasta(input_path) as input_file:
                for item in input_file:
                    if discard_duplicates:
                        if item.id not in identifiers:
                            output_file.write(item)
                        identifiers.add(item.id)
                    else:
                        output_file.write(item)


def batch_merge_fasta_files(
    input_path: Path,
    output_path: Path,
    matching_regex: str = r"^(\d+)",
    discard_duplicates: bool = True,
):
    if not input_path.exists():
        raise Exception("Input path does not exist.")
    if not input_path.is_dir():
        raise Exception("Input path is not a directory.")
    if not output_path.exists():
        raise Exception("Output path does not exist.")
    if not output_path.is_dir():
        raise Exception("Output path is not a directory.")

    groups = get_file_groups(input_path, matching_regex)

    for group, filenames in groups.items():
        input_paths = [input_path / filename for filename in filenames]
        merge_fasta_files(input_paths, output_path / f"{group}_merged.fasta", discard_duplicates)
