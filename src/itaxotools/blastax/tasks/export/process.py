import re
from pathlib import Path
from time import perf_counter

from ..common.process import StagingArea
from ..common.types import Confirmation, Results
from .types import DatabaseInfo


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


def _parse_database_version(info_output: str) -> int | None:
    for line in info_output.splitlines():
        match = re.search(r"BLASTDB Version:\s*(\d+)", line)
        if match:
            return int(match.group(1))
    return None


def _get_database_type(input_database_path: Path) -> str | None:
    if input_database_path.with_suffix(".nin").exists():
        return "nucleotide"
    elif input_database_path.with_suffix(".pin").exists():
        return "protein"
    return None


def database_check_info(
    work_dir: Path,
    input_database_path: Path,
):
    from itaxotools import abort, get_feedback, progress_handler
    from itaxotools.blastax.core import get_database_info, run_blast_export

    print(f"{input_database_path=}")

    db_type = _get_database_type(input_database_path)

    staging = StagingArea(work_dir)
    staging.add(db_paths=[input_database_path])
    if staging.requires_copy():
        if not get_feedback(Confirmation.StagingRequired):
            abort()

    progress_handler("Staging files", 0, 0, 0)
    staging.stage(verbose=True)

    try:
        progress_handler("Checking database info...", 0, 0, 0)
        info_bytes = get_database_info(
            database_path=staging[input_database_path],
            debug=True,
        )
        info_output = info_bytes.decode("utf-8")
        version = _parse_database_version(info_output)

        progress_handler("Checking taxonomy IDs...", 0, 0, 0)
        output_bytes = run_blast_export(
            database_path=staging[input_database_path],
            output_path=None,
            outfmt="%T",
            debug=True,
        )
        progress_handler("Done.", 1, 0, 1)
    finally:
        staging.cleanup()

    output = output_bytes.decode("utf-8")
    if not output.strip():
        has_taxids = None
    else:
        has_taxids = True
        for line in output.splitlines():
            if not line.strip() or line.strip() == "0":
                has_taxids = False
                break

    return DatabaseInfo(version, db_type, has_taxids)


def kraken_from_fasta(
    input_fasta_path: Path,
    output_fasta_path: Path,
    output_map_path: Path,
    taxid: str,
) -> Results:
    from itaxotools import abort, get_feedback, progress_handler
    from itaxotools.blastax.core import kraken_from_fasta

    print(f"{input_fasta_path=}")
    print(f"{output_fasta_path=}")
    print(f"{output_map_path=}")
    print(f"{taxid=}")

    if output_fasta_path.exists() or output_map_path.exists():
        if not get_feedback(Confirmation.OverwriteFiles):
            abort()

    ts = perf_counter()

    progress_handler("Running script", 0, 0, 0)
    kraken_from_fasta(
        input_fasta_path=input_fasta_path,
        output_fasta_path=output_fasta_path,
        output_map_path=output_map_path,
        taxid=taxid,
    )
    progress_handler("Done.", 1, 0, 1)

    tf = perf_counter()

    return Results(output_map_path.parent, tf - ts)


def taxid_map_from_fasta(
    input_fasta_path: Path,
    output_fasta_path: Path,
    output_map_path: Path,
) -> Results:
    from itaxotools import abort, get_feedback, progress_handler
    from itaxotools.blastax.core import taxid_map_from_fasta

    print(f"{input_fasta_path=}")
    print(f"{output_fasta_path=}")
    print(f"{output_map_path=}")

    if output_fasta_path.exists() or output_map_path.exists():
        if not get_feedback(Confirmation.OverwriteFiles):
            abort()

    ts = perf_counter()

    progress_handler("Running script", 0, 0, 0)
    taxid_map_from_fasta(
        input_fasta_path=input_fasta_path,
        output_fasta_path=output_fasta_path,
        output_map_path=output_map_path,
    )
    progress_handler("Done.", 1, 0, 1)

    tf = perf_counter()

    return Results(output_map_path.parent, tf - ts)
