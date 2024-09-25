#!/usr/bin/env python3

import argparse
import gzip
import os
import sys
import warnings
from typing import BinaryIO, Iterator, List, Optional, TextIO, cast

from fastutils import (
    Pattern,
    fasta_iter,
    fasta_iter_chunks,
    fastq_iter,
    fastq_iter_chunks,
    make_template,
    parse_pattern_optional,
    template_files,
)


def parse_size(s: str) -> Optional[int]:
    """
    Parses file size as number with a suffix in "bBkKmMgG", interpreted as a unit
    """
    num = s[:-1]
    suffix = s[-1]
    try:
        power = dict(b=0, k=1, m=2, g=3)[suffix.casefold()]
    except KeyError:
        return None
    return round(float(num) * (1024**power))


def list_bytes(chunk: List[str]) -> bytes:
    """
    converts a list of string into utf-8 encoded bytes
    """
    return b"".join(map(lambda s: bytes(s, "utf-8"), chunk))


def write_maxsize(chunks: Iterator[List[str]], maxsize: int, compressed: bool, output_template: str) -> None:
    """
    Writes chunks to the files based on the output_template, each file will be no bigger than maxsize.
    Each chunk will be written whole in some file.
    If 'compressed' each file will be compressed with gzip.
    """
    # generator of output files
    files = template_files(output_template, "wb", compressed)
    # keep track of written size
    current_size = 0
    # current output file
    current_file = cast(BinaryIO, next(files))

    for chunk in chunks:
        # convert the chunk into bytes
        bytes_to_write = list_bytes(chunk)
        if current_size + len(bytes_to_write) > maxsize:
            # if the current file would overflow, switch to a new file
            current_file = cast(BinaryIO, next(files))
            current_size = 0
        # write the bytes and add the written size
        current_file.write(bytes_to_write)
        current_size = current_size + len(bytes_to_write)
    # close the last file
    try:
        files.send("stop")
    except StopIteration:
        pass


def fastsplit(
    file_format: str,
    split_n: Optional[int],
    maxsize: Optional[int],
    seqid_pattern: Optional[str],
    sequence_pattern: Optional[str],
    infile_path: Optional[str],
    compressed: bool,
    outfile_template: Optional[str],
) -> None:
    if not infile_path:
        # raise error, if there is no input file
        raise ValueError("No input file")
    if infile_path.endswith(".gz"):
        infile = cast(TextIO, gzip.open(infile_path, mode="rt", errors="replace"))
    else:
        infile = open(infile_path, errors="replace")
    with infile:
        # prepare a valid output template
        if not outfile_template:
            outfile_template = make_template(infile_path)
        elif "#" not in outfile_template:
            outfile_template = make_template(outfile_template)
        if maxsize or split_n:
            # initialize the input file reader
            if file_format == "fasta":
                chunks = fasta_iter_chunks(infile)
            elif file_format == "fastq":
                chunks = fastq_iter_chunks(infile)
            elif file_format == "text":
                chunks = map(lambda s: [s], infile)
            else:
                chunks = None
        else:
            chunks = None
        # call subfunctions
        if maxsize:
            # split by maximum size
            assert chunks is not None
            write_maxsize(chunks, maxsize, compressed, outfile_template)
        elif split_n:
            # split by number of files
            # get the size of the input
            size = os.stat(infile_path).st_size
            # if split_n == 6, size == 42 gives maxsize == 7, size == 43 gives maxsize == 8, size 48 gives maxsize 8
            maxsize = (size - 1 + split_n) // split_n
            assert chunks is not None
            write_maxsize(chunks, maxsize, compressed, outfile_template)
        elif seqid_pattern or sequence_pattern:
            # split by patterns
            if file_format == "fasta":
                fastsplit_fasta_filter(
                    infile,
                    parse_pattern_optional(seqid_pattern),
                    parse_pattern_optional(sequence_pattern),
                    compressed,
                    outfile_template,
                )
            elif file_format == "fastq":
                fastsplit_fastq_filter(
                    infile,
                    parse_pattern_optional(seqid_pattern),
                    parse_pattern_optional(sequence_pattern),
                    compressed,
                    outfile_template,
                )
            else:
                raise ValueError("Pattern are not supported for text files")


def fastsplit_fasta_filter(
    infile: TextIO,
    seqid_pattern: Optional[Pattern],
    sequence_pattern: Optional[Pattern],
    compressed: bool,
    outfile_template: str,
) -> None:
    """
    splits a fasta file by patterns
    """
    # creates a function to open output files
    if compressed:

        def opener(name: str) -> TextIO:
            return cast(TextIO, gzip.open(name, mode="wt", errors="replace"))
    else:

        def opener(name: str) -> TextIO:
            return open(name, mode="w", errors="replace")

    # assemples names and open output files
    accepted_file, rejected_file = map(
        opener, map(lambda s: outfile_template.replace("#", s), ["_accepted", "_rejected"])
    )
    # create the records' stream
    records = fasta_iter(infile)
    # warn about the line breaks
    line_breaks_warned = False
    for seqid, sequence in records:
        if not line_breaks_warned and sequence_pattern and len(sequence) > 1:
            line_breaks_warned = True
            warnings.warn(
                f"The file {infile.name} contains sequences interrupted with line breaks, and the search for sequence motifs will not work reliably in this case - some sequences with the specified motif will likely be missed. Please first transform your file into a fasta file without line breaks interrupting the sequences."
            )
        # calculate of the record matches the pattern
        accepted = (seqid_pattern and seqid_pattern.match(seqid)) or (
            sequence_pattern and any(map(sequence_pattern.match, sequence))
        )
        # choose the output file
        if accepted:
            output = accepted_file
        else:
            output = rejected_file
        # write the record to the selected file
        output.write(seqid)
        for chunk in sequence:
            output.write(chunk)


def fastsplit_fastq_filter(
    infile: TextIO,
    seqid_pattern: Optional[Pattern],
    sequence_pattern: Optional[Pattern],
    compressed: bool,
    outfile_template: str,
) -> None:
    """
    splits a fastq file by patterns
    """
    # creates a function to open output files
    if compressed:

        def opener(name: str) -> TextIO:
            return cast(TextIO, gzip.open(name, mode="wt", errors="replace"))
    else:

        def opener(name: str) -> TextIO:
            return open(name, mode="w", errors="replace")

    # assemples names and open output files
    accepted_file, rejected_file = map(
        opener, map(lambda s: outfile_template.replace("#", s), ["_accepted", "_rejected"])
    )
    # create the records' stream
    records = fastq_iter(infile)
    for seqid, sequence, *quality in records:
        # calculate of the record matches the pattern
        accepted = (seqid_pattern and seqid_pattern.match(seqid)) or (
            sequence_pattern and sequence_pattern.match(sequence)
        )
        # choose the output file
        if accepted:
            output = accepted_file
        else:
            output = rejected_file
        # write the record to the selected file
        for line in [seqid, sequence, *quality]:
            output.write(line)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()

    format_group = argparser.add_mutually_exclusive_group()
    format_group.add_argument(
        "--fasta", dest="format", action="store_const", const="fasta", help="Input file is a fasta file"
    )
    format_group.add_argument(
        "--fastq", dest="format", action="store_const", const="fastq", help="Input file is a fastq file"
    )
    format_group.add_argument(
        "--text", dest="format", action="store_const", const="text", help="Input file is a text file"
    )

    split_group = argparser.add_mutually_exclusive_group()
    split_group.add_argument("--split_n", type=int, help="number of files to split into")
    split_group.add_argument("--maxsize", type=parse_size, help="Maximum size of output file")
    split_group.add_argument(
        "--seqid", metavar="PATTERN", help="split the records that match the sequence identifier pattern"
    )
    split_group.add_argument(
        "--sequence", metavar="PATTERN", help="split the records that match the sequence motif pattern"
    )

    argparser.add_argument("--compressed", action="store_true", help="Compress output files with gzip")
    argparser.add_argument("infile", nargs="?", help="Input file name")
    argparser.add_argument("outfile", nargs="?", help="outfile file template")

    args = argparser.parse_args()

    try:
        with warnings.catch_warnings(record=True) as warns:
            fastsplit(
                args.format,
                args.split_n,
                args.maxsize,
                args.seqid,
                args.sequence,
                args.infile,
                args.compressed,
                args.outfile,
            )
            for w in warns:
                print(w.message)
    except ValueError as ex:
        sys.exit(ex)
