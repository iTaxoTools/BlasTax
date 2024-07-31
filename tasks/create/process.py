from time import perf_counter
from typing import Literal

from .types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")


def execute(
    input_path: str,
    output_path: str,
    type: Literal["nucl", "prot"],
    name: str,
) -> Results:
    from core import make_database

    ts = perf_counter()
    make_database(
        input_path=input_path,
        output_path=output_path,
        type=type,
        name=name,
        version=4,
    )
    tf = perf_counter()

    return Results(None, tf - ts)
