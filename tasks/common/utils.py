from pathlib import Path


def get_database_index_from_path(path: Path) -> Path | None:
    if path.suffix in [
        ".ndb",
        ".nhr",
        ".nin",
        ".njs",
        ".nog",
        ".nos",
        ".not",
        ".nsd",
        ".nsi",
        ".nsq",
        ".ntf",
        ".nto",
    ]:
        return path.with_suffix("")

    if path.suffix in [
        ".pdb",
        ".phr",
        ".pin",
        ".pjs",
        ".pog",
        ".pos",
        ".pot",
        ".psd",
        ".psi",
        ".psq",
        ".ptf",
        ".pto",
    ]:
        return path.with_suffix("")

    return None
