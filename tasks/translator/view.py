from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import GLineEdit

from ..common.view import (
    BlastTaskView,
    GraphicTitleCard,
    OptionCard,
    PathDirectorySelector,
    PathFileSelector,
)
from . import long_description, pixmap_medium, title


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
        self.cards.template = FilenameSelector("Output filename", self)
        # self.cards.format = FileFormatSelector("Output format", self)
        self.cards.compress = OptionCard("Compress output", "", self)

        self.cards.input.set_placeholder_text("Sequence file that will be translated")
        self.cards.output.set_placeholder_text("Folder that will contain all output files")
        self.cards.template.set_placeholder_text("The resuulting translated protein filename")

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

        # self.binder.bind(object.properties.filename_template, self.cards.template.set_name)
        # self.binder.bind(self.cards.template.nameChanged, object.properties.filename_template)

        # self.binder.bind(object.properties.output_format, self.cards.format.set_value)
        # self.binder.bind(self.cards.format.valueChanged, object.properties.output_format)
        # self.binder.bind(object.properties.split_option, self.cards.format.set_option)
        # self.binder.bind(self.cards.format.optionChanged, object.properties.split_option)
        # self.binder.bind(object.properties.pattern_available, self.cards.format.set_pattern_available)

        # self.binder.bind(object.properties.compress, self.cards.compress.setChecked)
        # self.binder.bind(self.cards.compress.toggled, object.properties.compress)

        # self.cards.format.controls.max_size.bind_property(object.properties.max_size)
        # self.cards.format.controls.split_n.bind_property(object.properties.split_n)
        # self.cards.format.controls.pattern_identifier.bind_property(object.properties.pattern_identifier)
        # self.cards.format.controls.pattern_sequence.bind_property(object.properties.pattern_sequence)

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
