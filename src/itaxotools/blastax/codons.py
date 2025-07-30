from itertools import islice
from typing import Literal

from Bio.Data import CodonTable


def batched(sequence: str, n: int = 3):
    # batched('ABCDEFG', 3) → ABC DEF G
    iterator = iter(sequence)
    while batch := tuple(islice(iterator, n)):
        yield "".join(batch)


def get_names_string(names: list[str | None], exclude_sgc=True) -> str:
    if exclude_sgc:
        names = (name for name in names if isinstance(name, str) and not name.startswith("SGC"))
    return "; ".join(name for name in names if name is not None)


def get_codon_tables(exclude_sgc=True) -> dict[int, list[str]]:
    return {
        id: get_names_string(CodonTable.unambiguous_dna_by_id[id].names, exclude_sgc)
        for id in CodonTable.unambiguous_dna_by_id
    }


def get_stop_codons_for_table(id: int) -> list[str]:
    return CodonTable.unambiguous_dna_by_id[id].stop_codons


def find_stop_codon_in_sequence(sequence: str, table_id: int, reading_frame: Literal[1, 2, 3] = 1) -> int:
    """Returns the position of the first encountered stop codon, or -1 if none were found."""
    sequence = sequence.upper()
    sequence = sequence[reading_frame - 1 :]
    stop_codons = get_stop_codons_for_table(table_id)
    for pos, batch in enumerate(batched(sequence)):
        if batch in stop_codons:
            return pos * 3 + reading_frame - 1
    return -1


def count_stop_codons_for_all_frames_in_sequence(
    sequence: str, table_id: int
) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """
    Returns the number of stop codons detected for reading frames 1, 2, and 3 respectively,
    as well as the first encountered stop codon position for each frame.
    """
    sequence = sequence.upper()
    stop_codons = get_stop_codons_for_table(table_id)
    triplets = zip(sequence, sequence[1:], sequence[2:])
    codons = ("".join(nucleotides) for nucleotides in triplets)
    counts = [0, 0, 0]
    positions = [-1, -1, -1]
    for pos, codon in enumerate(codons):
        if codon in stop_codons:
            frame = pos % 3
            counts[frame] += 1
            if positions[frame] == -1:
                positions[frame] = pos
    return tuple(counts), tuple(positions)


def are_counts_ambiguous(counts: tuple[int, int, int]) -> bool:
    """Statistically, only one reading frame will lack stop codons."""
    return sum(x == 0 for x in counts) != 1


def smart_trim_sequence(
    sequence: str,
    counts: tuple[int, int, int],
    positions: tuple[int, int, int],
    trim_stop: bool = True,
    trim_end: bool = True,
) -> str | None:
    """
    Autodetect the best reading frame for a sequence by scanning for stop codons
    in different positions. Then trim the sequence at its beginning to start
    at the first codon position. Optionally trim at the end based on arguments.
    """
    frame = min(enumerate(counts), key=lambda x: x[1])[0]
    if trim_stop:
        end_pos = positions[frame]
        sequence = sequence[:end_pos]
    sequence = sequence[frame:]
    if trim_end:
        end_pos = len(sequence) - (len(sequence) % 3)
        sequence = sequence[:end_pos]
    return sequence


if __name__ == "__main__":
    tables = get_codon_tables()
    for id, name in tables.items():
        print(f"{(str(id) + ':').rjust(3)} {name}")
