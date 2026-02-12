from pathlib import Path
from time import perf_counter
from traceback import print_exc
from typing import Literal

from ..common.process import stage_paths, unstage_paths
from ..common.types import BatchResults


class IdentityDict(dict):
    def __missing__(self, key):
        return key


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.utils  # noqa


def execute(
    work_dir: Path,
    input_paths: list[Path],
    output_path: Path,
    type: Literal["nucl", "prot"],
    name: str,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler
    from itaxotools.blastax.core import get_error_filename

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{type=}")
    print(f"{name=}")

    total = len(input_paths)
    failed: list[Path] = []

    staged_paths = stage_paths(work_dir, input_paths, [output_path], dry=True)
    if staged_paths:
        if not get_feedback("STAGE"):
            abort()

    target_paths = [
        get_target_path(output_path, type, name if total == 1 else staged_paths[path].stem) for path in input_paths
    ]

    if any(path.exists() for path in target_paths):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    progress_handler("Staging files", 0, 0, 0)
    staged_paths = stage_paths(work_dir, input_paths, [output_path])

    for k, v in staged_paths.items():
        print(f"Staged {repr(k)} as {repr(v)}")

    try:
        for i, (path, target) in enumerate(zip(input_paths, target_paths)):
            progress_handler(f"Processing file {i+1}/{total}: {path.name}", i, 0, total)
            try:
                execute_single(
                    input_path=staged_paths[path],
                    output_path=staged_paths[output_path],
                    type=type,
                    name=name if total == 1 else staged_paths[path].stem,
                )
            except Exception as e:
                if total == 1:
                    raise e
                error_log_path = output_path / get_error_filename(path)
                with open(error_log_path, "w") as f:
                    print_exc(file=f)
                failed.append(path)
    finally:
        unstage_paths(work_dir, staged_paths, [output_path])

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_path, failed, tf - ts)


def execute_single(
    input_path: list[Path],
    output_path: Path,
    type: Literal["nucl", "prot"],
    name: str,
):
    from itaxotools.blastax.core import make_database
    from itaxotools.blastax.utils import check_fasta_headers

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
        debug=True,
    )


def get_target_path(output_path: Path, type: Literal["nucl", "prot"], name: str) -> Path:
    suffix = {"nucl": ".nin", "prot": ".pin"}[type]
    return Path(output_path / name).with_suffix(suffix)
