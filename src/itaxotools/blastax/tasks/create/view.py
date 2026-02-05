from PySide6 import QtCore, QtWidgets

from pathlib import Path
from typing import Literal

from itaxotools.common.bindings import Binder
from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import GLineEdit, LongLabel, RadioButtonGroup

from ..common.view import BatchProgressCard, BatchQuerySelector, BlastTaskView, GraphicTitleCard, PathDirectorySelector
from . import long_description, pixmap_medium, title


class NameSelector(Card):
    nameChanged = QtCore.Signal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.binder = Binder()
        self.draw_main(text)
        self.draw_warning()
        self.roll = VerticalRollAnimation(self)

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

    def draw_warning(self):
        warning = "WARNING:  For best results in downstream analysis, use short database names (10-20 characters) without spaces or special characters."
        label = LongLabel(warning)
        self.addWidget(label)

    def _handle_name_changed(self, name: str):
        self.nameChanged.emit(str(name))

    def set_placeholder_text(self, text: str):
        self.controls.field.setPlaceholderText(text)

    def set_name(self, name: str):
        text = name or ""
        self.controls.field.setText(text)


class TypeSelector(Card):
    typeChanged = QtCore.Signal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.binder = Binder()
        self.draw_main(text)

    def draw_main(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        nucl = QtWidgets.QRadioButton("Nucleotide sequences")
        prot = QtWidgets.QRadioButton("Protein sequences")

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_value_changed)
        group.add(nucl, "nucl")
        group.add(prot, "prot")

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(nucl)
        layout.addWidget(prot, 1)
        layout.addSpacing(136)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.label = label
        self.controls.nucl = nucl
        self.controls.prot = prot
        self.controls.type = group

    def _handle_value_changed(self, value):
        self.typeChanged.emit(str(value))

    def set_type(self, type: Literal["nucl", "prot"]):
        self.controls.type.setValue(type)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = BatchProgressCard(self)
        self.cards.input = BatchQuerySelector("Input sequences")
        self.cards.output_path = PathDirectorySelector("\u25C0  Output folder")
        self.cards.database_name = NameSelector("Database name")
        self.cards.database_type = TypeSelector("Database type")

        self.cards.input.set_placeholder_text("Sequences to go into the new database")
        self.cards.input.set_batch_placeholder_text("Sequences that each go into a new database")
        self.cards.database_name.set_placeholder_text("Determines filenames and title")
        self.cards.output_path.set_placeholder_text("Database files will be saved here")

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

        self.cards.input.bind_batch_model(self.binder, object.input)

        self.binder.bind(object.properties.output_path, self.cards.output_path.set_path)
        self.binder.bind(self.cards.output_path.selectedPath, object.properties.output_path)

        self.binder.bind(object.properties.database_name, self.cards.database_name.set_name)
        self.binder.bind(self.cards.database_name.nameChanged, object.properties.database_name)
        self.binder.bind(
            object.input.properties.batch_mode, self.cards.database_name.roll.setAnimatedVisible, lambda x: not x
        )

        self.binder.bind(object.properties.database_type, self.cards.database_type.set_type)
        self.binder.bind(self.cards.database_type.typeChanged, object.properties.database_type)

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
