from datetime import datetime
from os import devnull
from pathlib import Path
from time import perf_counter
from typing import TextIO

from .types import RemovalMode, RemovalResults


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.codons  # noqa
    import itaxotools.taxi2.sequences  # noqa


def execute(
    input_paths: Path,
    output_dir: Path,
    mode: RemovalMode,
    frame: int,
    code: int,
    cutoff: int,
    log: bool,
    append_timestamp: bool,
    append_configuration: bool,
) -> RemovalResults:
    from itaxotools import abort, get_feedback

    print(f"{input_paths=}")
    print(f"{output_dir=}")
    print(f"{mode=}")
    print(f"{frame=}")
    print(f"{code=}")
    print(f"{cutoff=}")
    print(f"{log=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    timestamp = datetime.now() if append_timestamp else None
    description: str = ""
    if append_configuration:
        description = "stops_removed"

    log_path = output_dir / "stop_codons.log" if log else devnull

    target_paths = [get_target_path(path, output_dir, description, timestamp) for path in input_paths]

    if any(path.exists() for path in target_paths) or (log and log_path.exists()):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    description: str = ""

    with open(log_path, "w") as log_file:
        log_options(log_file, code, frame)

        match mode:
            case RemovalMode.discard_file:
                description = execute_discard_file(
                    input_paths=input_paths,
                    target_paths=target_paths,
                    log_file=log_file,
                    frame=frame,
                    code=code,
                )

            case RemovalMode.discard_sequence:
                description = execute_discard_sequences(
                    input_paths=input_paths,
                    target_paths=target_paths,
                    log_file=log_file,
                    frame=frame,
                    code=code,
                )

            case RemovalMode.trim_after_stop:
                description = execute_trim_after_stop(
                    input_paths=input_paths,
                    target_paths=target_paths,
                    log_file=log_file,
                    frame=frame,
                    code=code,
                )

            case RemovalMode.trim_or_discard:
                description = execute_trim_or_discard(
                    input_paths=input_paths,
                    target_paths=target_paths,
                    log_file=log_file,
                    frame=frame,
                    code=code,
                    cutoff=cutoff,
                )

            case RemovalMode.report_only:
                description = execute_report_only(
                    input_paths=input_paths,
                    log_file=log_file,
                    frame=frame,
                    code=code,
                )

    tf = perf_counter()

    return RemovalResults(output_dir, description, tf - ts)


def log_options(file: TextIO, code: int, frame: int):
    from itaxotools.blastax.codons import get_codon_tables, get_stop_codons_for_table

    table = get_codon_tables()[code]
    stops = get_stop_codons_for_table(code)
    stops_str = ", ".join(stops)
    print("# Stop codon removal", file=file)
    print(file=file)
    print(f"Codon table:   {code} - {table}", file=file)
    print(f"Stop codons:   {stops_str}", file=file)
    print(f"Reading frame: {frame}", file=file)
    print(file=file)


def log_filename(file: TextIO, filename: str):
    print(f"- Filename: {filename}", file=file)
    print(file=file)


def log_stop_codon(file: TextIO, id: str, pos: int, codon: str):
    print(f"  * Seqid:    {id}", file=file)
    print(f"    Position: {pos+1}-{pos+3}", file=file)
    print(f"    Codon:    {codon}", file=file)
    print(file=file)


def execute_discard_file(
    input_paths: list[Path],
    target_paths: list[Path],
    log_file: TextIO,
    frame: int,
    code: int,
) -> str:
    import shutil

    from itaxotools.blastax.codons import find_stop_codon_in_sequence
    from itaxotools.taxi2.sequences import SequenceHandler

    def check_file_contains_stop_codon(path: Path) -> bool:
        with SequenceHandler.Fasta(path) as file:
            for sequence in file:
                pos = find_stop_codon_in_sequence(sequence=sequence.seq, table_id=code, reading_frame=frame)
                if pos >= 0:
                    codon = sequence.seq[pos : pos + 3]
                    log_filename(log_file, path.name)
                    log_stop_codon(log_file, sequence.id, pos, codon)
                    return True
        return False

    file_count = 0

    for input_path, target_path in zip(input_paths, target_paths):
        if not check_file_contains_stop_codon(input_path):
            shutil.copy(input_path, target_path)
        else:
            file_count += 1

    if not file_count:
        print("No stop codons detected!", file=log_file)

    s = "" if file_count == 1 else "s"
    return f"Discarded {file_count} file{s}"


def execute_discard_sequences(
    input_paths: list[Path],
    target_paths: list[Path],
    log_file: TextIO,
    frame: int,
    code: int,
) -> str:
    from itaxotools.blastax.codons import find_stop_codon_in_sequence
    from itaxotools.taxi2.sequences import SequenceHandler

    file_count = 0
    sequence_count = 0

    for input_path, target_path in zip(input_paths, target_paths):
        already_encountered = False
        with (
            SequenceHandler.Fasta(input_path) as input_file,
            SequenceHandler.Fasta(target_path, "w", line_width=0) as output_file,
        ):
            for sequence in input_file:
                pos = find_stop_codon_in_sequence(sequence=sequence.seq, table_id=code, reading_frame=frame)
                if pos < 0:
                    output_file.write(sequence)
                else:
                    codon = sequence.seq[pos : pos + 3]
                    sequence_count += 1
                    if not already_encountered:
                        log_filename(log_file, input_path.name)
                        already_encountered = True
                        file_count += 1
                    log_stop_codon(log_file, sequence.id, pos, codon)

    if not file_count:
        print("No stop codons detected!", file=log_file)

    ss = "" if sequence_count == 1 else "s"
    fs = "" if file_count == 1 else "s"
    return f"Discarded {sequence_count} sequence{ss} from {file_count} file{fs}"


def execute_trim_after_stop(
    input_paths: list[Path],
    target_paths: list[Path],
    log_file: TextIO,
    frame: int,
    code: int,
) -> str:
    from itaxotools.blastax.codons import find_stop_codon_in_sequence
    from itaxotools.taxi2.sequences import Sequence, SequenceHandler

    file_count = 0
    sequence_count = 0

    for input_path, target_path in zip(input_paths, target_paths):
        already_encountered = False
        with (
            SequenceHandler.Fasta(input_path) as input_file,
            SequenceHandler.Fasta(target_path, "w", line_width=0) as output_file,
        ):
            for sequence in input_file:
                pos = find_stop_codon_in_sequence(
                    sequence=sequence.seq,
                    table_id=code,
                    reading_frame=frame,
                )
                if pos >= 0:
                    codon = sequence.seq[pos : pos + 3]
                    sequence = Sequence(sequence.id, sequence.seq[:pos])
                    sequence_count += 1
                    if not already_encountered:
                        log_filename(log_file, input_path.name)
                        already_encountered = True
                        file_count += 1
                    log_stop_codon(log_file, sequence.id, pos, codon)
                output_file.write(sequence)

    if not file_count:
        print("No stop codons detected!", file=log_file)

    ss = "" if sequence_count == 1 else "s"
    fs = "" if file_count == 1 else "s"
    return f"Trimmed {sequence_count} sequence{ss} from {file_count} file{fs}"


def execute_trim_or_discard(
    input_paths: list[Path],
    target_paths: list[Path],
    log_file: TextIO,
    frame: int,
    code: int,
    cutoff: int,
) -> str:
    from itaxotools.blastax.codons import find_stop_codon_in_sequence
    from itaxotools.taxi2.sequences import Sequence, SequenceHandler

    file_count = 0
    discard_count = 0
    trim_count = 0

    for input_path, target_path in zip(input_paths, target_paths):
        already_encountered = False
        with (
            SequenceHandler.Fasta(input_path) as input_file,
            SequenceHandler.Fasta(target_path, "w", line_width=0) as output_file,
        ):
            for sequence in input_file:
                threshold = len(sequence.seq) - cutoff
                pos = find_stop_codon_in_sequence(
                    sequence=sequence.seq,
                    table_id=code,
                    reading_frame=frame,
                )
                if pos < 0:
                    output_file.write(sequence)
                else:
                    codon = sequence.seq[pos : pos + 3]
                    if pos >= threshold:
                        sequence = Sequence(sequence.id, sequence.seq[:pos])
                        output_file.write(sequence)
                        trim_count += 1
                    else:
                        discard_count += 1
                    if not already_encountered:
                        log_filename(log_file, input_path.name)
                        already_encountered = True
                        file_count += 1
                    log_stop_codon(log_file, sequence.id, pos, codon)

    if not file_count:
        print("No stop codons detected!", file=log_file)

    ds = "" if discard_count == 1 else "s"
    ts = "" if trim_count == 1 else "s"
    fs = "" if file_count == 1 else "s"
    return f"Discarded {discard_count} sequence{ds} and\ntrimmed {trim_count} sequence{ts} from {file_count} file{fs}"


def execute_report_only(
    input_paths: list[Path],
    log_file: TextIO,
    frame: int,
    code: int,
) -> str:
    from itaxotools.blastax.codons import find_stop_codon_in_sequence
    from itaxotools.taxi2.sequences import SequenceHandler

    file_count = 0
    sequence_count = 0

    for input_path in input_paths:
        already_encountered = False
        with SequenceHandler.Fasta(input_path) as input_file:
            for sequence in input_file:
                pos = find_stop_codon_in_sequence(
                    sequence=sequence.seq,
                    table_id=code,
                    reading_frame=frame,
                )
                if pos >= 0:
                    codon = sequence.seq[pos : pos + 3]
                    sequence_count += 1
                    if not already_encountered:
                        log_filename(log_file, input_path.name)
                        already_encountered = True
                        file_count += 1
                    log_stop_codon(log_file, sequence.id, pos, codon)

    if not file_count:
        print("No stop codons detected!", file=log_file)

    ss = "" if sequence_count == 1 else "s"
    fs = "" if file_count == 1 else "s"
    return f"Detected {sequence_count} codon{ss} in {file_count} file{fs}"


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
