from pathlib import Path
from time import perf_counter

from ..common.process import StagingArea
from ..common.types import Confirmation, Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.utils  # noqa


def database_to_fasta(
    work_dir: Path,
    input_database_path: Path,
    output_path: Path,
    blast_outfmt: str,
    blast_taxdb_path: Path,
) -> Results:
    from itaxotools import abort, get_feedback, progress_handler
    from itaxotools.blastax.core import run_blast_export

    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_outfmt=}")
    print(f"{blast_taxdb_path=}")

    blast_outfmt = blast_outfmt.encode().decode("unicode_escape")

    staging = StagingArea(work_dir)
    staging.add(output_paths=[output_path], db_paths=[input_database_path], taxdb_path=blast_taxdb_path)
    if staging.requires_copy():
        if not get_feedback(Confirmation.StagingRequired):
            abort()

    if output_path.exists():
        if not get_feedback(Confirmation.overwrite_file(output_path)):
            abort()

    ts = perf_counter()

    progress_handler("Staging files", 0, 0, 0)
    staging.stage(verbose=True)

    with staging:
        progress_handler("Running BLAST+", 0, 0, 0)
        run_blast_export(
            database_path=staging[input_database_path],
            output_path=staging[output_path],
            blastdb_path=staging[blast_taxdb_path],
            outfmt=blast_outfmt,
            debug=True,
        )
        progress_handler("Done.", 1, 0, 1)

    tf = perf_counter()

    return Results(output_path, tf - ts)


def database_check_taxid(
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
        if not get_feedback(Confirmation.StagingRequired):
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
        if not line.strip() or line.strip() == "0":
            return False

    return True
