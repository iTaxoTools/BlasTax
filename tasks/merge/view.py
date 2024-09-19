from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.bindings import Binder, PropertyRef
from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import RadioButtonGroup

from ..common.view import (
    BlastTaskView,
    GraphicTitleCard,
    PathDirectorySelector,
)
from ..common.widgets import (
    PropertyLineEdit,
)
from . import long_description, pixmap_medium, title


class RegexSelector(Card):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.binder = Binder()
        self.draw_main(text)

    def draw_main(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setStyleSheet("""font-size: 14px;""")
        label.setMinimumWidth(150)

        field = PropertyLineEdit()
        field.setTextMargins(4, 0, 12, 0)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(field, 1)
        layout.addSpacing(136)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.label = label
        self.controls.field = field

    def bind_property(self, property: PropertyRef):
        self.controls.field.bind_property(property)


class DiscardDuplicatesSelector(Card):
    valueChanged = QtCore.Signal(bool)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.draw_main(text)

    def draw_main(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setStyleSheet("""font-size: 14px;""")
        label.setMinimumWidth(150)

        first = QtWidgets.QRadioButton("Only keep first sequence")
        all = QtWidgets.QRadioButton("Keep all occurences")

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_value_changed)
        group.add(first, True)
        group.add(all, False)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(first)
        layout.addWidget(all, 1)
        layout.addSpacing(136)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.label = label
        self.controls.first = first
        self.controls.all = all
        self.controls.group = group

    def _handle_value_changed(self, value: bool):
        self.valueChanged.emit(value)

    def set_value(self, value: bool):
        self.controls.group.setValue(value)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.input = PathDirectorySelector("\u25B6  Input folder", self)
        self.cards.output = PathDirectorySelector("\u25C0  Output folder", self)
        self.cards.regex = RegexSelector("Matching regex")
        self.cards.duplicates = DiscardDuplicatesSelector("On duplicate identifiers")

        self.cards.input.set_placeholder_text("Folder that contains the FASTA files to be merged")
        self.cards.output.set_placeholder_text("All merged FASTA files will be saved here")

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
        self.binder.bind(self.cards.input.selectedPath, object.open)

        self.binder.bind(object.properties.output_path, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_path)

        self.binder.bind(object.properties.discard_duplicates, self.cards.duplicates.set_value)
        self.binder.bind(self.cards.duplicates.valueChanged, object.properties.discard_duplicates)

        self.cards.regex.bind_property(object.properties.matching_regex)

        self.binder.bind(object.properties.editable, self.setEditable)

    def setEditable(self, editable: bool):
        for card in self.cards:
            card.setEnabled(editable)
        self.cards.title.setEnabled(True)
        self.cards.progress.setEnabled(True)

    def open(self):
        filename = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self.window(),
            caption=f"{app.config.title} - Open folder",
        )
        if not filename:
            return
        self.object.open(Path(filename))
