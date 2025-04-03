from pathlib import Path
from time import perf_counter
from traceback import print_exc
from typing import Literal

from ..common.types import BatchResults


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import core  # noqa
    import utils  # noqa


def execute(
    input_paths: list[Path],
    output_path: Path,
    type: Literal["nucl", "prot"],
    name: str,
) -> BatchResults:
    from core import get_error_filename
    from itaxotools import abort, get_feedback, progress_handler

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{type=}")
    print(f"{name=}")

    total = len(input_paths)
    failed: list[Path] = []

    target_paths = [get_target_path(path, output_path, type) for path in input_paths]

    if any(path.exists() for path in target_paths):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    for i, (path, target) in enumerate(zip(input_paths, target_paths)):
        progress_handler(f"Processing file {i+1}/{total}: {path.name}", i, 0, total)
        try:
            execute_single(
                input_path=path,
                output_path=output_path,
                type=type,
                name=name if total == 1 else path.stem,
            )
        except Exception as e:
            if total == 1:
                raise e
            error_log_path = output_path / get_error_filename(path)
            with open(error_log_path, "w") as f:
                print_exc(file=f)
            failed.append(path)

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_path, failed, tf - ts)


def execute_single(
    input_path: list[Path],
    output_path: Path,
    type: Literal["nucl", "prot"],
    name: str,
):
    from core import make_database
    from utils import check_fasta_headers

    header_check_result = check_fasta_headers(str(input_path))
    if header_check_result == "length":
        raise Exception(
            "One or more sequence headers in the FASTA file exceed 51 characters! Please check and edit headers!"
        )
    elif header_check_result == "special":
        raise Exception(
            "One or more sequence headers in the FASTA file contain special characters! Please check and edit headers!"
        )

    make_database(
        input_path=str(input_path),
        output_path=str(output_path),
        type=type,
        name=name,
        version=4,
    )


def get_target_path(input_path: Path, output_path: Path, type: Literal["nucl", "prot"]) -> Path:
    suffix = {"nucl": ".nin", "prot": ".pin"}[type]
    return output_path / input_path.with_suffix(suffix).name
