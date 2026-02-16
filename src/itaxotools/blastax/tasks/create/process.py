from pathlib import Path
from time import perf_counter
from traceback import print_exc
from typing import Literal

from ..common.process import StagingArea
from ..common.types import BatchResults


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
    taxid_map_path: Path,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler
    from itaxotools.blastax.core import get_error_filename

    if taxid_map_path == Path() or len(input_paths) > 1:
        taxid_map_path = None

    print(f"{input_paths=}")
    print(f"{output_path=}")
    print(f"{type=}")
    print(f"{name=}")
    print(f"{taxid_map_path=}")

    total = len(input_paths)
    failed: list[Path] = []

    taxid_map_paths = [taxid_map_path] if taxid_map_path else []

    staging = StagingArea(work_dir)
    staging.add(input_paths=input_paths + taxid_map_paths, output_paths=[output_path])

    if staging.requires_copy():
        if not get_feedback("STAGE"):
            abort()

    target_paths = [
        get_target_path(output_path, type, name if total == 1 else staging[path].stem) for path in input_paths
    ]

    if any(path.exists() for path in target_paths):
        if not get_feedback(None):
            abort()

    ts = perf_counter()

    progress_handler("Staging files", 0, 0, 0)
    staging.stage()

    for original, staged in staging.items():
        print(f"Staged {repr(original)} as {repr(staged)}")

    with staging:
        for i, (path, target) in enumerate(zip(input_paths, target_paths)):
            progress_handler(f"Processing file {i+1}/{total}: {path.name}", i, 0, total)
            try:
                execute_single(
                    input_path=staging[path],
                    output_path=staging[output_path],
                    type=type,
                    name=name if total == 1 else staging[path].stem,
                    taxid_map_path=staging[taxid_map_path] if taxid_map_path else None,
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
    taxid_map_path: Path | None = None,
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
        taxid_map_path=str(taxid_map_path) if taxid_map_path else None,
        debug=True,
    )


def get_target_path(output_path: Path, type: Literal["nucl", "prot"], name: str) -> Path:
    suffix = {"nucl": ".nin", "prot": ".pin"}[type]
    return Path(output_path / name).with_suffix(suffix)
