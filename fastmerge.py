#!/usr/bin/env python3

import argparse
import gzip
import os
import sys
import warnings
from typing import Callable, Iterable, Iterator, Optional, Set, TextIO, Union, cast

from fastutils import (
    Pattern,
    ext_gz,
    fasta_iter,
    fastq_iter,
    parse_pattern_optional,
)

# extensions of the fasta files
fasta_exts = {".fas", ".fasta"}
# extensions of the fastq files
fastq_exts = {".fq", ".fastq"}


def fastmerge(
    file_list: Iterable[str],
    file_types: Optional[Set[str]],
    seqid_pattern: str,
    sequence_pattern: str,
    output: TextIO,
    progress_callback: Callable[[str, int, int], None] = None,
) -> None:
    """
    Main merging function
    """
    if not file_types:
        fastmerge_pure(file_list, output, progress_callback)
    else:
        if seqid_pattern or sequence_pattern:
            if ".fas" in file_types:
                fastmerge_fasta_filter(
                    file_list, parse_pattern_optional(seqid_pattern), parse_pattern_optional(sequence_pattern), output
                )
            else:
                fastmerge_fastq_filter(
                    file_list, parse_pattern_optional(seqid_pattern), parse_pattern_optional(sequence_pattern), output
                )
        else:
            fastmerge_type(file_list, file_types, output)


def list_files(file_list: Iterable[str]) -> Iterator[Union[str, os.DirEntry]]:
    """
    For each file in 'file_list' yield its name.
    For each directory, yields the DirEnty of file inside it
    """
    for filename in file_list:
        filename = filename.strip()
        if os.path.isdir(filename):
            for entry in filter(os.DirEntry.is_file, os.scandir(filename)):
                yield entry
        elif os.path.exists(filename):
            yield filename


def fastmerge_pure(
    file_list: Iterable[str], output: TextIO, progress_callback: Callable[[str, int, int], None] = None
) -> None:
    """
    Merge the files, extracting all gzip archives
    """
    for i, entry in enumerate(list_files(file_list)):
        if progress_callback:
            progress_callback(entry, i, len(file_list))
        # open the file as archive or text file
        if os.path.splitext(entry)[1] == ".gz":
            file = cast(TextIO, gzip.open(entry, mode="rt", errors="replace"))
        else:
            file = open(entry, errors="replace")
        # copy the lines to the output
        with file:
            for line in file:
                print(line.rstrip(), file=output)


def fastmerge_type(
    file_list: Iterable[str],
    file_types: Set[str],
    output: TextIO,
    progress_callback: Callable[[str, int, int], None] = None,
) -> None:
    """
    Merge the file only of the given 'file_types', extracting all gzip archives
    """
    for i, entry in enumerate(list_files(file_list)):
        if progress_callback:
            progress_callback(entry, i, len(file_list))
        # skip the files of the wrong type
        if ext_gz(entry) not in file_types:
            continue
        # open the file as archive or text file
        if os.path.splitext(entry)[1] == ".gz":
            file = cast(TextIO, gzip.open(entry, mode="rt", errors="replace"))
        else:
            file = open(entry, errors="replace")
        # copy the lines to the output
        with file:
            for line in file:
                print(line.rstrip(), file=output)


def fastmerge_fasta_filter(
    file_list: Iterable[str],
    seqid_pattern: Optional[Pattern],
    sequence_pattern: Optional[Pattern],
    output: TextIO,
    progress_callback: Callable[[str, int, int], None] = None,
) -> None:
    """
    Merge the fasta files, extraction all gzip archives.
    Filter records with the given patterns
    """
    for i, entry in enumerate(list_files(file_list)):
        if progress_callback:
            progress_callback(entry, i, len(file_list))
        # skip the files of the wrong type
        if ext_gz(entry) not in fasta_exts:
            continue
        # copy the lines to the output
        if os.path.splitext(entry)[1] == ".gz":
            file = cast(TextIO, gzip.open(entry, mode="rt", errors="replace"))
        else:
            file = open(entry, errors="replace")
        with file:
            # warn about the line breaks
            line_breaks_warned = False
            for seqid, sequence in fasta_iter(file):
                if not line_breaks_warned and sequence_pattern and len(sequence) > 1:
                    line_breaks_warned = True
                    warnings.warn(
                        f"The file {file.name} contains sequences interrupted with line breaks, and the search for sequence motifs will not work reliably in this case - some sequences with the specified motif will likely be missed. Please first transform your file into a fasta file without line breaks interrupting the sequences."
                    )
                # skip sequences that don't match the seqid pattern
                if seqid_pattern:
                    if not seqid_pattern.match(seqid):
                        continue
                # skip sequences that don't match the sequence pattern
                if sequence_pattern:
                    if not any(map(sequence_pattern.match, sequence)):
                        continue
                # copy the lines into the output
                print(seqid.rstrip(), file=output)
                for chunk in sequence:
                    print(chunk.rstrip(), file=output)


def fastmerge_fastq_filter(
    file_list: Iterable[str],
    seqid_pattern: Optional[Pattern],
    sequence_pattern: Optional[Pattern],
    output: TextIO,
    progress_callback: Callable[[str, int, int], None] = None,
) -> None:
    """
    Merge the fastq files, extraction all gzip archives.
    Filter records with the given patterns
    """
    for i, entry in enumerate(list_files(file_list)):
        if progress_callback:
            progress_callback(entry, i, len(file_list))
        # skip the files of the wrong type
        if ext_gz(entry) not in fastq_exts:
            continue
        # copy the lines to the output
        if os.path.splitext(entry)[1] == ".gz":
            file = cast(TextIO, gzip.open(entry, mode="rt", errors="replace"))
        else:
            file = open(entry, errors="replace")
        with file:
            for seqid, sequence, quality_score_seqid, quality_score in fastq_iter(file):
                # skip sequences that don't match the seqid pattern
                if seqid_pattern:
                    if not seqid_pattern.match(seqid):
                        continue
                # skip sequences that don't match the sequence pattern
                if sequence_pattern:
                    if not sequence_pattern.match(sequence):
                        continue
                print(seqid.rstrip(), file=output)
                print(sequence.rstrip(), file=output)
                print(quality_score_seqid.rstrip(), file=output)
                print(quality_score.rstrip(), file=output)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--cmd", action="store_true", help="Launches in the command-line mode")
    format_group = argparser.add_mutually_exclusive_group()
    format_group.add_argument(
        "--fasta", dest="ext", action="store_const", const=fasta_exts, help="Process only .fas and .fas.gz files"
    )
    format_group.add_argument(
        "--fastq",
        dest="ext",
        action="store_const",
        const=fastq_exts,
        help="Process only .fq, .fq.gz, .fastq and .fastq.gz files",
    )
    argparser.add_argument("--seqid", metavar="PATTERN", help="Filter pattern for sequence names")
    argparser.add_argument("--sequence", metavar="PATTERN", help="Filter pattern for sequences")

    args = argparser.parse_args()

    try:
        with warnings.catch_warnings(record=True) as warns:
            fastmerge(sys.stdin, args.ext, args.seqid, args.sequence, sys.stdout)
            for w in warns:
                print(w.message)
    except ValueError as ex:
        sys.exit(ex)
