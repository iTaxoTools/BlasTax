import pytest

from itaxotools.blastax.tasks import (
    about,
    append,
    appendx,
    blast,
    codon_align,
    create,
    cutadapt,
    decont,
    download,
    export,
    fastmerge,
    fastsplit,
    groupmerge,
    mafft,
    museo,
    prepare,
    removal,
    scafos,
    taxo,
    taxodecont,
    translator,
    trim,
)
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.main import Main


def test_main(qapp):
    Main()


@pytest.mark.parametrize("module", [
    about,
    append,
    appendx,
    blast,
    codon_align,
    create,
    cutadapt,
    decont,
    download,
    export,
    fastmerge,
    fastsplit,
    groupmerge,
    mafft,
    museo,
    prepare,
    removal,
    scafos,
    taxo,
    taxodecont,
    translator,
    trim,
], ids=lambda m: m.__name__.split(".")[-1])
def test_task(qapp, module):
    task = app.Task.from_module(module)
    task.view()
    model = task.model()
    model.close()
