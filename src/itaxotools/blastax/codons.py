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


if __name__ == "__main__":
    tables = get_codon_tables()
    for id, name in tables.items():
        print(f"{(str(id) + ':').rjust(3)} {name}")
