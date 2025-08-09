from datetime import datetime
from pathlib import Path
from time import perf_counter

from ..common.types import Results
from ..mafft.types import AdjustDirection, AlignmentStrategy


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.utils  # noqa


def execute(
    work_dir: Path,
    input_paths: list[Path],
    output_path: Path,
    codon_table: int,
    strategy: AlignmentStrategy,
    adjust_direction: AdjustDirection,
    append_timestamp: bool,
    append_configuration: bool,
) -> Results:
    from itaxotools import abort, get_feedback, progress_handler

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{codon_table=}")
    print(f"{strategy=}")
    print(f"{adjust_direction=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_paths)

    timestamp = datetime.now() if append_timestamp else None
    configuration: dict[str, str] = {}
    if append_configuration:
        configuration[strategy.key] = None
        if adjust_direction.option:
            configuration[adjust_direction.option] = None

    target_paths = [get_target_path(input_path, output_path, timestamp, configuration) for input_path in input_paths]

    if any((path.exists() for path in target_paths)):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (input_path, target_path) in enumerate(zip(input_paths, target_paths)):
        progress_handler(f"Processing file {i+1}/{total}: {input_path.name}", i, 0, total)
        single_work_dir = work_dir / input_path.name
        single_work_dir.mkdir()
        execute_single(
            work_dir=single_work_dir,
            input_path=input_path,
            target_path=target_path,
            codon_table=codon_table,
            strategy=strategy,
            adjust_direction=adjust_direction,
        )

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return Results(output_path, tf - ts)


def execute_single(
    work_dir: Path,
    input_path: Path,
    target_path: Path,
    codon_table: int,
    strategy: AlignmentStrategy,
    adjust_direction: AdjustDirection,
):
    from Bio.Seq import Seq

    from itaxotools.blastax.codons import batched
    from itaxotools.mafftpy import MultipleSequenceAlignment
    from itaxotools.taxi2.sequences import Sequence, SequenceHandler

    translated_path = work_dir / input_path.name

    input_sequences: list[Sequence] = []

    with (
        SequenceHandler.Fasta(input_path) as input_file,
        SequenceHandler.Fasta(translated_path, "w", line_width=0) as translated_file,
    ):
        for sequence in input_file:
            input_sequences.append(sequence)
            codons = Seq(sequence.seq).translate(table=codon_table)
            codon_sequence = Sequence(id=sequence.id, seq=str(codons), extras=sequence.extras)
            translated_file.write(codon_sequence)

    a = MultipleSequenceAlignment(translated_path)
    a.vars.set_strategy(strategy.key)
    a.vars.set_adjust_direction(adjust_direction.key)
    a.target = work_dir

    a.run()
    aligned_path = a.get_results_path()

    with (
        SequenceHandler.Fasta(aligned_path) as aligned_file,
        SequenceHandler.Fasta(target_path, "w", line_width=0) as target_file,
    ):
        for input_sequence, aligned_sequence in zip(input_sequences, aligned_file):
            assert input_sequence.id == aligned_sequence.id
            batches = batched(input_sequence.seq)

            def get_next_nucleotides(codon: str) -> str:
                if codon == "-":
                    return "---"
                return next(batches)

            nucleotides = "".join(get_next_nucleotides(codon) for codon in aligned_sequence.seq)
            nucleotide_sequence = Sequence(id=input_sequence.id, seq=nucleotides, extras=input_sequence.extras)

            target_file.write(nucleotide_sequence)


def get_target_path(
    input_path: Path,
    output_dir: Path,
    timestamp: datetime | None,
    configuration: dict[str, str],
) -> Path:
    from itaxotools.blastax.core import get_output_filename

    return output_dir / get_output_filename(
        input_path=input_path,
        suffix=".fasta",
        description="codons_aligned",
        timestamp=timestamp,
        **configuration,
    )
