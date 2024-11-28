from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import GLineEdit, RadioButtonGroup, RichRadioButton

from ..common.view import (
    BlastTaskView,
    GraphicTitleCard,
    OptionCard,
    PathDirectorySelector,
    PathFileSelector,
)
from . import long_description, pixmap_medium, title
from .types import TranslationMode


class FilenameSelector(Card):
    nameChanged = QtCore.Signal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.draw_main(text)

    def draw_main(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        field = GLineEdit()
        field.textEditedSafe.connect(self._handle_name_changed)
        field.setPlaceholderText("---")
        field.setTextMargins(4, 0, 12, 0)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(field, 1)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.label = label
        self.controls.field = field

    def _handle_name_changed(self, name: str):
        self.nameChanged.emit(str(name))

    def set_placeholder_text(self, text: str):
        self.controls.field.setPlaceholderText(text)

    def set_name(self, name: str):
        text = name or ""
        self.controls.field.setText(text)


class ModeSelector(Card):
    mode_changed = QtCore.Signal(TranslationMode)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.draw_main(text)

    def draw_main(self, text):
        title = QtWidgets.QLabel(text + ":")
        title.setStyleSheet("""font-size: 16px;""")
        title.setMinimumWidth(150)

        mode_layout = QtWidgets.QVBoxLayout()
        mode_layout.setSpacing(8)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_mode_changed)

        for mode in TranslationMode:
            button = RichRadioButton(mode.label + ":", mode.description)
            group.add(button, mode)
            mode_layout.addWidget(button)

        self.controls.mode = group

        self.addWidget(title)
        self.addLayout(mode_layout)

    def _handle_mode_changed(self, value: bool):
        self.mode_changed.emit(value)

    def set_mode(self, value: bool):
        self.controls.mode.setValue(value)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.input = PathFileSelector("\u25C0  Input file", self)
        self.cards.output = PathDirectorySelector("\u25C0  Output folder", self)
        self.cards.output_filename = FilenameSelector("Output filename", self)
        self.cards.mode = ModeSelector("Translation mode", self)
        self.cards.compress = OptionCard("Compress output", "", self)

        self.cards.input.set_placeholder_text("Sequence file that will be translated")
        self.cards.output.set_placeholder_text("Folder that will contain all output files")
        self.cards.output_filename.set_placeholder_text("The resulting protein sequence filename")

        layout = QtWidgets.QVBoxLayout()
        for card in self.cards:
            layout.addWidget(card)
        layout.addStretch(1)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        self.setLayout(layout)

    def setObject(self, object):
        self.object = object
        self.binder.unbind_all()

        self.binder.bind(object.notification, self.showNotification)
        self.binder.bind(object.report_results, self.report_results)
        self.binder.bind(object.request_confirmation, self.request_confirmation)
        self.binder.bind(object.progression, self.cards.progress.showProgress)

        self.binder.bind(object.properties.name, self.cards.title.setTitle)
        self.binder.bind(object.properties.busy, self.cards.progress.setVisible)

        self.binder.bind(object.properties.input_path, self.cards.input.set_path)
        self.binder.bind(self.cards.input.selectedPath, object.properties.input_path)

        self.binder.bind(object.properties.output_path, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_path)

        self.binder.bind(object.properties.output_filename, self.cards.output_filename.set_name)
        self.binder.bind(self.cards.output_filename.nameChanged, object.properties.output_filename)

        self.binder.bind(object.properties.option_mode, self.cards.mode.set_mode)
        self.binder.bind(self.cards.mode.mode_changed, object.properties.option_mode)

        self.binder.bind(object.properties.editable, self.setEditable)

    def setEditable(self, editable: bool):
        for card in self.cards:
            card.setEnabled(editable)
        self.cards.title.setEnabled(True)
        self.cards.progress.setEnabled(True)

    def open(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=self.window(),
            caption=f"{app.config.title} - Open file",
        )
        if not filename:
            return
        self.object.open(Path(filename))
