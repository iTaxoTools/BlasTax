from .types import Results


def initialize():
    import itaxotools

    itaxotools.progress_handler("Initializing...")
    from . import work  # noqa


def execute() -> Results:
    return Results(None, 0.0)
