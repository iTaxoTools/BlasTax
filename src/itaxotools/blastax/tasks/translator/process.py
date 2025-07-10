from pathlib import Path
from time import perf_counter
from traceback import print_exc

from ..common.types import BatchResults, Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    import itaxotools.blastax.translator  # noqa


def execute(
    input_path: Path,
    output_path: Path,
    log_path: Path,
    nucleotide_path: Path,
    input_type: str,
    frame: str,
    code: int,
) -> Results:
    from itaxotools.blastax.translator import Options, translate

    print(f"{input_path=}")
    print(f"{output_path=}")
    print(f"{log_path=}")
    print(f"{nucleotide_path=}")
    print(f"{input_type=}")
    print(f"{frame=}")
    print(f"{code=}")

    ts = perf_counter()

    options = Options(
        input_path=input_path,
        output_path=output_path,
        log_path=log_path,
        nucleotide_path=nucleotide_path,
        input_type=input_type,
        frame=frame,
        code=code,
    )
    translate(options)

    tf = perf_counter()

    return Results(output_path, tf - ts)


def execute_batch(
    input_paths: list[Path],
    output_dir: Path,
    write_logs: bool,
    write_nucleotides: bool,
    input_type: str,
    frame: str,
    code: int,
) -> Results:
    from itaxotools import progress_handler
    from itaxotools.blastax.core import get_error_filename
    from itaxotools.blastax.translator import Options, translate

    print(f"{input_paths=}")
    print(f"{output_dir=}")
    print(f"{write_logs=}")
    print(f"{write_nucleotides=}")
    print(f"{input_type=}")
    print(f"{frame=}")
    print(f"{code=}")

    total = len(input_paths)
    failed: list[Path] = []

    ts = perf_counter()

    for i, input_path in enumerate(input_paths):
        progress_handler(f"Processing file {i}/{total}: {input_path.name}", i, 0, total)
        output_path = output_dir / input_path.with_stem(input_path.stem + "_aa").with_suffix(".fasta").name
        log_path = output_dir / input_path.with_suffix(".log").name if write_logs else None
        error_path = output_dir / get_error_filename(input_path)
        if input_type == "transcript" and write_nucleotides:
            nucleotide_path = output_dir / input_path.with_stem(Path(input_path).stem + "_orf_nt").name
        else:
            nucleotide_path = None
        options = Options(
            input_path=input_path,
            output_path=output_path,
            log_path=log_path,
            nucleotide_path=nucleotide_path,
            input_type=input_type,
            frame=frame,
            code=code,
        )
        try:
            translate(options)
        except Exception:
            with open(error_path, "w") as f:
                print_exc(file=f)
            failed.append(input_path)

    progress_handler("Done processing files.", total, 0, total)

    tf = perf_counter()

    return BatchResults(output_dir, failed, tf - ts)


def dummy() -> Results:
    raise NotImplementedError()
