from PySide6 import QtCore, QtGui

from enum import Enum
from pathlib import Path

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


documents = LazyResourceCollection(
    about=lambda: text_from_path(get_data("documents/about.html")),
    blast=lambda: text_from_path(get_data("documents/blast.html")),
    museo=lambda: text_from_path(get_data("documents/museo.html")),
    version=lambda: text_from_path(get_data("documents/version.txt")).strip(),
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
    rename=lambda: VectorPixmap(get_data("graphics/rename.svg"), Size.Large.size),
    merge=lambda: VectorPixmap(get_data("graphics/merge.svg"), Size.Large.size),
)


task_pixmaps_medium = LazyResourceCollection(
    about=lambda: VectorPixmap(get_data("graphics/about.svg"), Size.Medium.size),
    create=lambda: VectorPixmap(get_data("graphics/create.svg"), Size.Medium.size),
    blast=lambda: VectorPixmap(get_data("graphics/blast.svg"), Size.Medium.size),
    append=lambda: VectorPixmap(get_data("graphics/append.svg"), Size.Medium.size),
    appendx=lambda: VectorPixmap(get_data("graphics/appendx.svg"), Size.Medium.size),
    museo=lambda: VectorPixmap(get_data("graphics/museo.svg"), Size.Medium.size),
    decont=lambda: VectorPixmap(get_data("graphics/decont.svg"), Size.Medium.size),
    rename=lambda: VectorPixmap(get_data("graphics/rename.svg"), Size.Medium.size),
    merge=lambda: VectorPixmap(get_data("graphics/merge.svg"), Size.Medium.size),
)
