from pathlib import Path
from time import perf_counter

from .types import RemovalMode, RemovalResults


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.codons  # noqa
    import itaxotools.taxi2.sequences  # noqa


def execute(
    input_paths: Path,
    output_dir: Path,
    mode: RemovalMode,
    frame: str,
    code: int,
) -> RemovalResults:
    import shutil

    from itaxotools import abort, get_feedback
    from itaxotools.blastax.codons import find_stop_codon_in_sequence
    from itaxotools.taxi2.sequences import Sequence, SequenceHandler

    print(f"{input_paths=}")
    print(f"{output_dir=}")
    print(f"{mode=}")
    print(f"{frame=}")
    print(f"{code=}")

    if any(Path(output_dir / path.name).exists() for path in input_paths):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    description: str = ""

    match mode:
        case RemovalMode.discard_file:

            def check_file_contains_stop_codon(path: Path) -> bool:
                with SequenceHandler.Fasta(path) as file:
                    for sequence in file:
                        if find_stop_codon_in_sequence(sequence=sequence.seq, table_id=code, reading_frame=frame) >= 0:
                            return True
                return False

            file_count = 0

            for path in input_paths:
                if not check_file_contains_stop_codon(path):
                    shutil.copy(path, output_dir / path.name)
                else:
                    file_count += 1

            s = "" if file_count == 1 else "s"
            description = f"Discarded {file_count} file{s}"

        case RemovalMode.discard_sequence:
            file_count = 0
            sequence_count = 0

            for input_path in input_paths:
                output_path = output_dir / input_path.name
                already_encountered = False
                with (
                    SequenceHandler.Fasta(input_path) as input_file,
                    SequenceHandler.Fasta(output_path, "w") as output_file,
                ):
                    for sequence in input_file:
                        if find_stop_codon_in_sequence(sequence=sequence.seq, table_id=code, reading_frame=frame) < 0:
                            output_file.write(sequence)
                        else:
                            sequence_count += 1
                            if not already_encountered:
                                already_encountered = True
                                file_count += 1

            ss = "" if sequence_count == 1 else "s"
            fs = "" if file_count == 1 else "s"
            description = f"Discarded {sequence_count} sequence{ss} from {file_count} file{fs}"

        case RemovalMode.trim_after_stop:
            file_count = 0
            sequence_count = 0

            for input_path in input_paths:
                output_path = output_dir / input_path.name
                already_encountered = False
                with (
                    SequenceHandler.Fasta(input_path) as input_file,
                    SequenceHandler.Fasta(output_path, "w") as output_file,
                ):
                    for sequence in input_file:
                        pos = find_stop_codon_in_sequence(
                            sequence=sequence.seq,
                            table_id=code,
                            reading_frame=frame,
                        )
                        if pos >= 0:
                            sequence = Sequence(sequence.id, sequence.seq[:pos])
                            sequence_count += 1
                            if not already_encountered:
                                already_encountered = True
                                file_count += 1
                        output_file.write(sequence)

            ss = "" if sequence_count == 1 else "s"
            fs = "" if file_count == 1 else "s"
            description = f"Trimmed {sequence_count} sequence{ss} from {file_count} file{fs}"

    tf = perf_counter()

    return RemovalResults(output_dir, description, tf - ts)
