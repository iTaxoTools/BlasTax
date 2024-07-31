from PySide6 import QtCore, QtGui, QtWidgets

from pathlib import Path

from itaxotools.common.bindings import Binder
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import GLineEdit

from .widgets import ElidedLineEdit


class GraphicTitleCard(Card):
    def __init__(self, title, description, pixmap, parent=None):
        super().__init__(parent)

        label_title = QtWidgets.QLabel(title)
        font = label_title.font()
        font.setPixelSize(18)
        font.setBold(True)
        font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1)
        label_title.setFont(font)

        label_description = QtWidgets.QLabel(description)
        label_description.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        label_description.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        label_description.setWordWrap(True)

        label_pixmap = QtWidgets.QLabel()
        label_pixmap.setPixmap(pixmap)
        label_pixmap.setFixedSize(pixmap.size())

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setContentsMargins(0, 6, 0, 4)
        text_layout.addWidget(label_title)
        text_layout.addWidget(label_description, 1)
        text_layout.setSpacing(8)

        pixmap_layout = QtWidgets.QVBoxLayout()
        pixmap_layout.setContentsMargins(0, 8, 0, 4)
        pixmap_layout.addWidget(label_pixmap)
        pixmap_layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(16)
        layout.addLayout(pixmap_layout)
        layout.addLayout(text_layout, 1)
        layout.addSpacing(100)

        self.addLayout(layout)

        self.controls.title = label_title
        self.controls.description = label_description
        self.controls.pixmap = label_pixmap

    def setTitle(self, text):
        self.controls.title.setText(text)

    def setBusy(self, busy: bool):
        self.setEnabled(not busy)


class PathSelector(Card):
    pathChanged = QtCore.Signal(Path)
    selectedPath = QtCore.Signal(Path)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.draw_main(text)

    def draw_main(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(140)

        field = ElidedLineEdit()
        field.textEditedSafe.connect(self._handle_text_changed)
        field.setReadOnly(True)

        browse = QtWidgets.QPushButton("Browse")
        browse.clicked.connect(self._handle_browse)
        browse.setFixedWidth(120)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(field, 1)
        layout.addWidget(browse)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.label = label
        self.controls.field = field
        self.controls.browse = browse

    def _handle_browse(self, *args):
        raise NotImplementedError()

    def _handle_text_changed(self, text: str):
        self.pathChanged.emit(Path(text))

    def set_busy(self, busy: bool):
        self.setEnabled(True)
        self.controls.field.setEnabled(not busy)
        self.controls.browse.setEnabled(not busy)
        self.controls.label.setEnabled(not busy)

    def set_path(self, path: Path):
        text = str(path) if path != Path() else "---"
        self.controls.field.setText(text)


class PathFileSelector(PathSelector):
    def _handle_browse(self, *args):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self.window(), f"{app.config.title} - Browse file")
        if not filename:
            return
        self.selectedPath.emit(Path(filename))


class PathDirectorySelector(PathSelector):
    def _handle_browse(self, *args):
        filename = QtWidgets.QFileDialog.getExistingDirectory(self.window(), f"{app.config.title} - Browse directory")
        if not filename:
            return
        self.selectedPath.emit(Path(filename))


class NameSelector(Card):
    nameChanged = QtCore.Signal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.binder = Binder()
        self.draw_main(text)

    def draw_main(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(140)

        field = GLineEdit()
        field.textEditedSafe.connect(self._handle_name_changed)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(field, 1)
        layout.addSpacing(136)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.label = label
        self.controls.field = field

    def _handle_browse(self, *args):
        raise NotImplementedError()

    def _handle_name_changed(self, name: str):
        self.nameChanged.emit(str(name))

    def set_busy(self, busy: bool):
        self.setEnabled(True)
        self.controls.field.setEnabled(not busy)
        self.controls.browse.setEnabled(not busy)
        self.controls.label.setEnabled(not busy)

    def set_name(self, name: str):
        text = name or "---"
        self.controls.field.setText(text)
