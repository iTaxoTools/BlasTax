from PySide6 import QtCore, QtGui

from enum import Enum
from pathlib import Path
from typing import Iterator

from itaxotools.common.widgets import VectorPixmap
from itaxotools.taxi_gui.app import skin
from itaxotools.taxi_gui.app.resources import LazyResourceCollection


class Size(Enum):
    Large = QtCore.QSize(128, 128)
    Medium = QtCore.QSize(64, 64)
    Small = QtCore.QSize(16, 16)

    def __init__(self, size):
        self.size = size


def get_data(path: str):
    here = Path(__file__).parent
    return str(here / path)


def text_from_path(path) -> str:
    with open(path, "r") as file:
        return file.read()


def lines_from_path(path) -> Iterator[str]:
    for line in open(path).readlines():
        yield line


documents = LazyResourceCollection(
    about=lambda: text_from_path(get_data("documents/about.html")),
    blast=lambda: text_from_path(get_data("documents/blast.html")),
    museo=lambda: text_from_path(get_data("documents/museo.html")),
)


icons = LazyResourceCollection(
    blastax=lambda: QtGui.QIcon(get_data("logos/blastax.ico")),
)


pixmaps = LazyResourceCollection(
    blastax=lambda: VectorPixmap(
        get_data("logos/blastax_banner.svg"),
        size=QtCore.QSize(170, 48),
        colormap=skin.colormap_icon,
    ),
)


task_pixmaps_large = LazyResourceCollection(
    about=lambda: VectorPixmap(get_data("graphics/about.svg"), Size.Large.size),
    create=lambda: VectorPixmap(get_data("graphics/create.svg"), Size.Large.size),
    blast=lambda: VectorPixmap(get_data("graphics/blast.svg"), Size.Large.size),
    append=lambda: VectorPixmap(get_data("graphics/append.svg"), Size.Large.size),
    appendx=lambda: VectorPixmap(get_data("graphics/appendx.svg"), Size.Large.size),
    museo=lambda: VectorPixmap(get_data("graphics/museo.svg"), Size.Large.size),
    decont=lambda: VectorPixmap(get_data("graphics/decont.svg"), Size.Large.size),
    prepare=lambda: VectorPixmap(get_data("graphics/prepare.svg"), Size.Large.size),
    fastmerge=lambda: VectorPixmap(get_data("graphics/fastmerge.svg"), Size.Large.size),
    fastsplit=lambda: VectorPixmap(get_data("graphics/fastsplit.svg"), Size.Large.size),
    groupmerge=lambda: VectorPixmap(get_data("graphics/groupmerge.svg"), Size.Large.size),
    scafos=lambda: VectorPixmap(get_data("graphics/scafos.svg"), Size.Large.size),
    translator=lambda: VectorPixmap(get_data("graphics/translator.svg"), Size.Large.size),
    removal=lambda: VectorPixmap(get_data("graphics/removal.svg"), Size.Large.size),
    trim=lambda: VectorPixmap(get_data("graphics/trim.svg"), Size.Large.size),
)


task_pixmaps_medium = LazyResourceCollection(
    about=lambda: VectorPixmap(get_data("graphics/about.svg"), Size.Medium.size),
    create=lambda: VectorPixmap(get_data("graphics/create.svg"), Size.Medium.size),
    blast=lambda: VectorPixmap(get_data("graphics/blast.svg"), Size.Medium.size),
    append=lambda: VectorPixmap(get_data("graphics/append.svg"), Size.Medium.size),
    appendx=lambda: VectorPixmap(get_data("graphics/appendx.svg"), Size.Medium.size),
    museo=lambda: VectorPixmap(get_data("graphics/museo.svg"), Size.Medium.size),
    decont=lambda: VectorPixmap(get_data("graphics/decont.svg"), Size.Medium.size),
    prepare=lambda: VectorPixmap(get_data("graphics/prepare.svg"), Size.Medium.size),
    fastmerge=lambda: VectorPixmap(get_data("graphics/fastmerge.svg"), Size.Medium.size),
    fastsplit=lambda: VectorPixmap(get_data("graphics/fastsplit.svg"), Size.Medium.size),
    groupmerge=lambda: VectorPixmap(get_data("graphics/groupmerge.svg"), Size.Medium.size),
    scafos=lambda: VectorPixmap(get_data("graphics/scafos.svg"), Size.Medium.size),
    translator=lambda: VectorPixmap(get_data("graphics/translator.svg"), Size.Medium.size),
    removal=lambda: VectorPixmap(get_data("graphics/removal.svg"), Size.Medium.size),
    trim=lambda: VectorPixmap(get_data("graphics/trim.svg"), Size.Medium.size),
)
