from pathlib import Path
from time import perf_counter

from ..common.process import StagingArea
from ..common.types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.utils  # noqa


def execute(
    work_dir: Path,
    input_database_path: Path,
    output_path: Path,
    blast_outfmt: str,
) -> Results:
    from itaxotools import abort, get_feedback, progress_handler
    from itaxotools.blastax.core import run_blast_export

    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_outfmt=}")

    blast_outfmt = blast_outfmt.encode().decode("unicode_escape")

    staging = StagingArea(work_dir)
    staging.add(output_paths=[output_path], db_paths=[input_database_path])
    if staging.requires_copy():
        if not get_feedback("STAGE"):
            abort()

    if output_path.exists():
        if not get_feedback(output_path):
            abort()

    ts = perf_counter()

    progress_handler("Staging files", 0, 0, 0)
    staging.stage(verbose=True)

    with staging:
        progress_handler("Running BLAST+", 0, 0, 0)
        run_blast_export(
            database_path=staging[input_database_path],
            output_path=staging[output_path],
            outfmt=blast_outfmt,
            debug=True,
        )
        progress_handler("Done.", 1, 0, 1)

    tf = perf_counter()

    return Results(output_path, tf - ts)


def check(
    work_dir: Path,
    input_database_path: Path,
) -> Results:
    from itaxotools import abort, get_feedback, progress_handler
    from itaxotools.blastax.core import run_blast_export

    print(f"{input_database_path=}")

    blast_outfmt = "%T"

    staging = StagingArea(work_dir)
    staging.add(db_paths=[input_database_path])
    if staging.requires_copy():
        if not get_feedback("STAGE"):
            abort()

    progress_handler("Staging files", 0, 0, 0)
    staging.stage(verbose=True)

    try:
        progress_handler("Running BLAST+", 0, 0, 0)
        output_bytes = run_blast_export(
            database_path=staging[input_database_path],
            output_path=None,
            outfmt=blast_outfmt,
            debug=True,
        )
        progress_handler("Done.", 1, 0, 1)
    finally:
        staging.cleanup()

    output = output_bytes.decode("utf-8")
    if not output.strip():
        return None

    for line in output.splitlines():
        print(">>>", repr(line))
        if not line.strip() or line.strip() == "0":
            return False

    return True
