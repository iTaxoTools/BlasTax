from pathlib import Path
from time import perf_counter
from typing import Literal

from ..common.types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    input_path: Path,
    output_path: Path,
    type: Literal["nucl", "prot"],
    name: str,
) -> Results:
    from core import make_database
    from utils import check_fasta_headers

    ts = perf_counter()

    header_check_result = check_fasta_headers(str(input_path))
    if header_check_result == "length":
        raise Exception(
            "One or more sequence headers in the FASTA file exceed 51 characters! Please check and edit headers!"
        )
    elif header_check_result == "special":
        raise Exception(
            "One or more sequence headers in the FASTA file contain special characters! Please check and edit headers!"
        )

    if not make_database(
        input_path=str(input_path),
        output_path=str(output_path),
        type=type,
        name=name,
        version=4,
    ):
        raise Exception("Database creation failed!")
    tf = perf_counter()

    return Results(output_path, tf - ts)
