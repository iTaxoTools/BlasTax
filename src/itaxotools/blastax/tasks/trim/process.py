from datetime import datetime
from os import devnull
from pathlib import Path
from time import perf_counter
from typing import TextIO

from .types import TrimResults


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.codons  # noqa
    import itaxotools.taxi2.sequences  # noqa


def execute(
    input_paths: Path,
    output_dir: Path,
    trim_stop: bool,
    trim_end: bool,
    discard_ambiguous: bool,
    code: int,
    log: bool,
    append_timestamp: bool,
    append_configuration: bool,
) -> TrimResults:
    from itaxotools import abort, get_feedback
    from itaxotools.blastax.codons import (
        are_counts_ambiguous,
        count_stop_codons_for_all_frames_in_sequence,
        smart_trim_sequence,
    )
    from itaxotools.taxi2.sequences import Sequence, SequenceHandler

    print(f"{input_paths=}")
    print(f"{output_dir=}")
    print(f"{trim_stop=}")
    print(f"{trim_end=}")
    print(f"{discard_ambiguous=}")
    print(f"{code=}")
    print(f"{log=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    timestamp = datetime.now() if append_timestamp else None
    description: str = ""
    if append_configuration:
        description = "trimmed"

    log_path = output_dir / "ambiguous_sequences.log" if log else devnull

    target_paths = [get_target_path(path, output_dir, description, timestamp) for path in input_paths]

    if any(path.exists() for path in target_paths) or (log and log_path.exists()):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    description: str = ""

    with open(log_path, "w") as log_file:
        log_options(log_file, code)
        file_count = 0
        ambiguity_count = 0

        for input_path, target_path in zip(input_paths, target_paths):
            already_encountered = False
            with (
                SequenceHandler.Fasta(input_path) as input_file,
                SequenceHandler.Fasta(target_path, "w", line_width=0) as output_file,
            ):
                for sequence in input_file:
                    counts, positions = count_stop_codons_for_all_frames_in_sequence(
                        sequence=sequence.seq,
                        table_id=code,
                    )
                    ambiguous = are_counts_ambiguous(counts)
                    if ambiguous:
                        ambiguity_count += 1
                        if not already_encountered:
                            log_filename(log_file, input_path.name)
                            already_encountered = True
                            file_count += 1
                        log_ambiguity(log_file, sequence.id, counts, positions)
                        if discard_ambiguous:
                            continue
                    seq = smart_trim_sequence(
                        sequence.seq,
                        counts=counts,
                        positions=positions,
                        trim_stop=trim_stop,
                        trim_end=trim_end,
                    )
                    sequence = Sequence(sequence.id, seq)
                    output_file.write(sequence)

        if not file_count:
            description = "No reading frame ambiguity detected!"
            print(description, file=log_file)

        ss = "y" if ambiguity_count == 1 else "ies"
        fs = "" if file_count == 1 else "s"
        description = f"Encountered {ambiguity_count} ambiguit{ss} in {file_count} file{fs}"

    tf = perf_counter()

    return TrimResults(output_dir, description, tf - ts)


def log_options(file: TextIO, code: int):
    from itaxotools.blastax.codons import get_codon_tables, get_stop_codons_for_table

    table = get_codon_tables()[code]
    stops = get_stop_codons_for_table(code)
    stops_str = ", ".join(stops)
    print("# Codon trimming", file=file)
    print(file=file)
    print(f"Codon table: {code} - {table}", file=file)
    print(f"Stop codons: {stops_str}", file=file)
    print(file=file)


def log_filename(file: TextIO, filename: str):
    print(f"- Filename: {filename}", file=file)
    print(file=file)


def log_ambiguity(file: TextIO, id: str, counts: tuple, positions: tuple):
    pos1 = positions[0] + 1 if positions[0] > 0 else "-"
    pos2 = positions[1] + 1 if positions[1] > 0 else "-"
    pos3 = positions[2] + 1 if positions[2] > 0 else "-"
    print(f"  * Seqid: {id}", file=file)
    print("    1st frame:  ", file=file)
    print(f"    + Number of stops: {counts[0]}", file=file)
    print(f"    + First position:  {pos1}", file=file)
    print("    2nd frame:  ", file=file)
    print(f"    + Number of stops: {counts[1]}", file=file)
    print(f"    + First position:  {pos2}", file=file)
    print("    3rd frame:  ", file=file)
    print(f"    + Number of stops: {counts[2]}", file=file)
    print(f"    + First position:  {pos3}", file=file)
    print(file=file)


def get_target_path(
    input_path: Path,
    output_dir: Path,
    description: str | None,
    timestamp: datetime | None,
) -> Path:
    from itaxotools.blastax.core import get_output_filename

    return output_dir / get_output_filename(
        input_path=input_path,
        suffix=".fasta",
        description=description,
        timestamp=timestamp,
    )
