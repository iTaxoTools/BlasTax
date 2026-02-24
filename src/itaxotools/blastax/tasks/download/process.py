from pathlib import Path
from time import perf_counter

from ..common.types import Results


def execute(output_path: Path) -> Results:
    from itaxotools import progress_handler
    from itaxotools.blastax.download import get_extras

    def progress_callback(downloaded, total):
        progress_handler("Downloading...", downloaded, 0, total)

    ts = perf_counter()

    get_extras(target=output_path, handler=progress_callback)

    progress_handler("Done.", 1, 0, 1)

    tf = perf_counter()

    return Results(output_path, tf - ts)
