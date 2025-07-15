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
    sequence = sequence[reading_frame - 1 :]
    stop_codons = get_stop_codons_for_table(table_id)
    for pos, batch in enumerate(batched(sequence)):
        if batch in stop_codons:
            return pos * 3 + reading_frame - 1
    return -1


if __name__ == "__main__":
    tables = get_codon_tables()
    for id, name in tables.items():
        print(f"{(str(id) + ':').rjust(3)} {name}")
