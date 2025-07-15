from ..common.types import Results


def get_blast_version() -> Results:
    from itaxotools.blastax.blast import get_blast_version

    try:
        return get_blast_version()
    except Exception:
        return None
