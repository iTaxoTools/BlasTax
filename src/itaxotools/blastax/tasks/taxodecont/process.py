from datetime import datetime
from pathlib import Path
from time import perf_counter
from traceback import print_exc

from itaxotools.blastax.utils import make_str_blast_safe

from ..common.process import StagingArea
from ..common.types import BatchResults, Confirmation
from .types import TargetPaths

BLAST_OUTFMT_OPTIONS = "qseqid sseqid pident bitscore length staxids"


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.core  # noqa
    import itaxotools.blastax.utils  # noqa


def execute(
    work_dir: Path,
    input_query_paths: list[Path],
    input_database_path: Path,
    output_path: Path,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    blast_taxdb_path: Path,
    taxid_mode_text: bool,
    taxid_text: str,
    taxid_path: Path | None,
    taxid_negative: bool,
    taxid_expand: bool,
    threshold_pident: float | None,
    threshold_bitscore: float | None,
    threshold_length: float | None,
    append_timestamp: bool,
    append_configuration: bool,
) -> BatchResults:
    from itaxotools import abort, get_feedback, progress_handler

    blast_outfmt_options = BLAST_OUTFMT_OPTIONS

    taxid_text = parse_taxid_text(taxid_text)

    print(f"{input_query_paths=}")
    print(f"{input_database_path=}")
    print(f"{output_path=}")
    print(f"{blast_method=}")
    print(f"{blast_evalue=}")
    print(f"{blast_num_threads=}")
    print(f"{blast_taxdb_path=}")
    print(f"{taxid_mode_text=}")
    print(f"{taxid_text=}")
    print(f"{taxid_path=}")
    print(f"{taxid_negative=}")
    print(f"{taxid_expand=}")
    print(f"{threshold_pident=}")
    print(f"{threshold_bitscore=}")
    print(f"{threshold_length=}")
    print(f"{append_timestamp=}")
    print(f"{append_configuration=}")

    total = len(input_query_paths)
    failed: list[Path] = []

    timestamp = datetime.now() if append_timestamp else None

    blast_options: dict[str, str] = {}
    decont_options: dict[str, str] = {}
    if append_configuration:
        blast_options[blast_method] = None
        if taxid_mode_text and taxid_text:
            if taxid_negative:
                blast_options["negative_taxids"] = None
            else:
                blast_options["taxids"] = None
            if not taxid_expand:
                blast_options["no_taxid_expansion"] = None
        if not taxid_mode_text and taxid_path:
            if taxid_negative:
                blast_options["negative_taxidlist"] = None
            else:
                blast_options["taxidlist"] = None
            if not taxid_expand:
                blast_options["no_taxid_expansion"] = None
        blast_options["evalue"] = blast_evalue
        parts = blast_outfmt_options.split(" ")
        blast_options["columns"] = "_".join(parts)
        if threshold_pident is not None:
            decont_options["pident"] = threshold_pident
        if threshold_bitscore is not None:
            decont_options["bitscore"] = threshold_bitscore
        if threshold_length is not None:
            decont_options["length"] = threshold_length

    target_paths_list = [
        get_target_paths(path, output_path, timestamp, blast_options, decont_options) for path in input_query_paths
    ]

    staging = StagingArea(work_dir)
    staging.add(
        input_paths=[taxid_path] if not taxid_mode_text else [],
        db_paths=[input_database_path],
        taxdb_path=blast_taxdb_path,
    )
    if staging.requires_copy():
        if not get_feedback(Confirmation.StagingRequired):
            abort()

    if any((path.exists() for target_paths in target_paths_list for path in target_paths)):
        if not get_feedback(Confirmation.OverwriteFiles):
            abort()

    ts = perf_counter()

    progress_handler("Staging database", 0, 0, 0)
    staging.stage(verbose=True)

    try:
        for i, (path, target) in enumerate(zip(input_query_paths, target_paths_list)):
            progress_handler(f"Processing file {i+1}/{total}: {path.name}", i, 0, total)
            try:
                execute_single(
                    work_dir=work_dir,
                    staging=staging,
                    input_query_path=path,
                    input_database_path=input_database_path,
                    blast_output_path=target.blast_output_path,
                    decontaminated_path=target.decontaminated_path,
                    contaminants_path=target.contaminants_path,
                    blast_method=blast_method,
                    blast_evalue=blast_evalue,
                    blast_num_threads=blast_num_threads,
                    blast_taxdb_path=blast_taxdb_path,
                    taxid_mode_text=taxid_mode_text,
                    taxid_text=taxid_text,
                    taxid_path=taxid_path,
                    taxid_negative=taxid_negative,
                    taxid_expand=taxid_expand,
                    threshold_pident=threshold_pident,
                    threshold_bitscore=threshold_bitscore,
                    threshold_length=threshold_length,
                )
            except Exception as e:
                if total == 1:
                    raise e
                with open(target.error_log_path, "w") as f:
                    print_exc(file=f)
                failed.append(path)
    finally:
        staging.cleanup()

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_path, failed, tf - ts)


def parse_taxid_text(text: str) -> str:
    ids = []
    for line in text.splitlines():
        for part in line.replace(",", " ").split():
            part = part.strip()
            if part:
                ids.append(part)
    return ",".join(ids) if ids else ""


def execute_single(
    work_dir: Path,
    staging: StagingArea,
    input_query_path: Path,
    input_database_path: Path,
    blast_output_path: Path,
    decontaminated_path: Path,
    contaminants_path: Path,
    blast_method: str,
    blast_evalue: float,
    blast_num_threads: int,
    blast_taxdb_path: Path,
    taxid_mode_text: bool,
    taxid_text: str,
    taxid_path: Path | None,
    taxid_negative: bool,
    taxid_expand: bool,
    threshold_pident: float | None,
    threshold_bitscore: float | None,
    threshold_length: float | None,
):
    from itaxotools.blastax.core import run_blast
    from itaxotools.blastax.utils import fastq_to_fasta, is_fastq, remove_gaps

    if is_fastq(input_query_path):
        target_query_path = work_dir / input_query_path.with_suffix(".fasta").name
        fastq_to_fasta(input_query_path, target_query_path)
        input_query_path = target_query_path

    stem = make_str_blast_safe(input_query_path.stem) + "_no_gaps"
    input_query_path_no_gaps = work_dir / input_query_path.with_stem(stem).name
    remove_gaps(input_query_path, input_query_path_no_gaps)

    staging.add(output_paths=[blast_output_path])
    staging.stage()

    blast_outfmt = f"6 {BLAST_OUTFMT_OPTIONS}"

    other = ""
    if taxid_mode_text and taxid_text:
        if taxid_negative:
            other += f"-negative_taxids {taxid_text} "
        else:
            other += f"-taxids {taxid_text} "
        if not taxid_expand:
            other += "-no_taxid_expansion"
    if not taxid_mode_text and taxid_path:
        if taxid_negative:
            other += f"-negative_taxidlist '{str(staging[taxid_path])}' "
        else:
            other += f"-taxidlist '{str(staging[taxid_path])}' "
        if not taxid_expand:
            other += "-no_taxid_expansion"

    try:
        run_blast(
            blast_binary=blast_method,
            query_path=input_query_path_no_gaps,
            database_path=staging[input_database_path],
            output_path=staging[blast_output_path],
            evalue=blast_evalue,
            num_threads=blast_num_threads,
            outfmt=blast_outfmt,
            other=other,
            blastdb_path=staging[blast_taxdb_path],
            debug=True,
        )

        contaminant_ids = get_contaminant_ids(
            blast_path=staging[blast_output_path],
            threshold_pident=threshold_pident,
            threshold_bitscore=threshold_bitscore,
            threshold_length=threshold_length,
        )

        write_decontaminated(
            query_path=input_query_path,
            contaminant_ids=contaminant_ids,
            decontaminated_path=decontaminated_path,
            contaminants_path=contaminants_path,
        )
    finally:
        staging.unstage_outputs()


def get_contaminant_ids(
    blast_path: Path,
    threshold_pident: float | None,
    threshold_bitscore: float | None,
    threshold_length: float | None,
) -> set[str]:
    from itaxotools.taxi2.handlers import FileHandler

    contaminant_ids: set[str] = set()

    with FileHandler.Tabfile(blast_path) as blast_file:
        for line in blast_file:
            qseqid = line[0]
            pident = float(line[2])
            bitscore = float(line[3])
            length = float(line[4])

            meets_all = True
            if threshold_pident is not None and pident < threshold_pident:
                meets_all = False
            if threshold_bitscore is not None and bitscore < threshold_bitscore:
                meets_all = False
            if threshold_length is not None and length < threshold_length:
                meets_all = False

            if meets_all:
                contaminant_ids.add(qseqid)

    return contaminant_ids


def write_decontaminated(
    query_path: Path,
    contaminant_ids: set[str],
    decontaminated_path: Path,
    contaminants_path: Path,
):
    from itaxotools.taxi2.sequences import SequenceHandler

    with (
        SequenceHandler.Fasta(query_path) as query_file,
        SequenceHandler.Fasta(decontaminated_path, "w", line_width=0) as decontaminated_file,
        SequenceHandler.Fasta(contaminants_path, "w", line_width=0) as contaminants_file,
    ):
        for item in query_file:
            if item.id in contaminant_ids:
                contaminants_file.write(item)
            else:
                decontaminated_file.write(item)


def get_target_paths(
    query_path: Path,
    output_path: Path,
    timestamp: datetime | None,
    blast_options: dict[str, str],
    decont_options: dict[str, str],
) -> TargetPaths:
    from itaxotools.blastax.core import get_blast_filename, get_decont_sequences_filename, get_error_filename

    blast_output_path = output_path / get_blast_filename(query_path, outfmt=6, timestamp=timestamp, **blast_options)
    decontaminated_path = output_path / get_decont_sequences_filename(
        query_path,
        "decontaminated",
        timestamp=timestamp,
        **decont_options,
    )
    contaminants_path = output_path / get_decont_sequences_filename(
        query_path,
        "contaminants",
        timestamp=timestamp,
        **decont_options,
    )
    error_log_path = output_path / get_error_filename(query_path, timestamp=timestamp)
    return TargetPaths(
        blast_output_path=blast_output_path,
        decontaminated_path=decontaminated_path,
        contaminants_path=contaminants_path,
        error_log_path=error_log_path,
    )
