from PySide6 import QtCore, QtGui

from pathlib import Path

from itaxotools.common.widgets import VectorPixmap
from itaxotools.taxi_gui.app import skin
from itaxotools.taxi_gui.app.resources import LazyResourceCollection


def get_data(path: str):
    here = Path(__file__).parent
    return str(here / path)


icons = LazyResourceCollection(
    blast=lambda: QtGui.QIcon(get_data("logos/blast.ico")),
)


pixmaps = LazyResourceCollection(
    blast=lambda: VectorPixmap(
        get_data("logos/blast.svg"),
        size=QtCore.QSize(192, 48),
        colormap=skin.colormap_icon,
    ),
)
