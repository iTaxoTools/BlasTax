from PySide6 import QtCore, QtGui, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.widgets import NoWheelComboBox

from ..common.view import (
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OptionCard,
    OutputDirectorySelector,
)
from ..common.widgets import (
    IntPropertyLineEdit,
    PropertyLineEdit,
)
from . import long_description, pixmap_medium, title
from .types import Direction


class PositionCombobox(NoWheelComboBox):
    valueChanged = QtCore.Signal(Direction)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = QtGui.QStandardItemModel()
        for pos in Direction:
            item = QtGui.QStandardItem()
            item.setData(pos.name, QtCore.Qt.DisplayRole)
            item.setData(pos, QtCore.Qt.UserRole)
            model.appendRow(item)
        self.setModel(model)

        self.currentIndexChanged.connect(self._handle_index_changed)

    def _handle_index_changed(self, index):
        self.valueChanged.emit(self.itemData(index, QtCore.Qt.UserRole))

    def setValue(self, value):
        index = self.findData(value, QtCore.Qt.UserRole)
        self.setCurrentIndex(index)


class SanitizeOptionCard(OptionCard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.draw_options()

    def draw_options(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        field = QtWidgets.QCheckBox(' Preserve any species separators ("@" and/or "|")')
        layout.addWidget(field, 1)
        self.controls.preserve_separators = field

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.roll = VerticalRollAnimation(widget)
        self.controls.options_widget = widget

        self.toggled.connect(self.set_options_visible)

        self.addWidget(widget)

    def set_options_visible(self, value: bool):
        self.controls.options_widget.roll.setAnimatedVisible(value)


class AddOptionCard(OptionCard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.draw_options()

    def draw_options(self):
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setColumnMinimumWidth(0, 8)
        layout.setColumnMinimumWidth(1, 72)
        layout.setColumnStretch(3, 1)
        layout.setHorizontalSpacing(32)
        layout.setVerticalSpacing(8)
        row = 0

        name = QtWidgets.QLabel("Text:")
        field = PropertyLineEdit()
        description = QtWidgets.QLabel("Text to add to all identifiers")
        description.setStyleSheet("QLabel { font-style: italic; }")
        layout.addWidget(name, row, 1)
        layout.addWidget(field, row, 2)
        layout.addWidget(description, row, 3)
        self.controls.text = field
        row += 1

        name = QtWidgets.QLabel("Direction:")
        field = PositionCombobox()
        description = QtWidgets.QLabel("Direction from which to trim characters")
        description.setStyleSheet("QLabel { font-style: italic; }")
        layout.addWidget(name, row, 1)
        layout.addWidget(field, row, 2)
        layout.addWidget(description, row, 3)
        self.controls.direction = field
        row += 1

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.roll = VerticalRollAnimation(widget)
        self.controls.options_widget = widget

        self.toggled.connect(self.set_options_visible)

        self.addWidget(widget)

    def set_options_visible(self, value: bool):
        self.controls.options_widget.roll.setAnimatedVisible(value)


class TrimOptionCard(OptionCard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.draw_options()

    def draw_options(self):
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setColumnMinimumWidth(0, 8)
        layout.setColumnMinimumWidth(1, 72)
        layout.setColumnStretch(3, 1)
        layout.setHorizontalSpacing(32)
        layout.setVerticalSpacing(8)
        row = 0

        name = QtWidgets.QLabel("Max length:")
        field = IntPropertyLineEdit()
        description = QtWidgets.QLabel("Maximum allowed number of characters")
        description.setStyleSheet("QLabel { font-style: italic; }")
        layout.addWidget(name, row, 1)
        layout.addWidget(field, row, 2)
        layout.addWidget(description, row, 3)
        self.controls.max_length = field
        row += 1

        name = QtWidgets.QLabel("Direction:")
        field = PositionCombobox()
        description = QtWidgets.QLabel("Direction from which to trim characters")
        description.setStyleSheet("QLabel { font-style: italic; }")
        layout.addWidget(name, row, 1)
        layout.addWidget(field, row, 2)
        layout.addWidget(description, row, 3)
        self.controls.direction = field
        row += 1

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.roll = VerticalRollAnimation(widget)
        self.controls.options_widget = widget

        self.toggled.connect(self.set_options_visible)

        self.addWidget(widget)

    def set_options_visible(self, value: bool):
        self.controls.options_widget.roll.setAnimatedVisible(value)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.query = BatchQuerySelector("Sequence files", self)
        self.cards.output = OutputDirectorySelector("\u25C0  Output folder", self)
        self.cards.sanitize = SanitizeOptionCard(
            "Sanitize",
            "Replace special characters with their ASCII representation, or an underscore if not applicable.",
        )
        self.cards.add = AddOptionCard(
            "Add text",
            "Add the specified text to each identifier.",
        )
        self.cards.auto_increment = OptionCard(
            "Auto increment",
            "Append a unique number at the end of each identifier, reflecting its position in the dataset.",
        )
        self.cards.trim = TrimOptionCard(
            "Trim",
            "Trim each identifier to fit within a specified character length.",
        )

        self.cards.query.set_placeholder_text("Sequences for which the identifiers will be renamed")
        self.cards.output.controls.append_configuration.setVisible(False)

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

        self.cards.query.bind_batch_model(self.binder, object.input_sequences)

        self.binder.bind(object.properties.output_path, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_path)

        self.binder.bind(object.properties.append_timestamp, self.cards.output.controls.append_timestamp.setChecked)
        self.binder.bind(self.cards.output.controls.append_timestamp.toggled, object.properties.append_timestamp)

        self.binder.bind(object.properties.sanitize, self.cards.sanitize.setChecked)
        self.binder.bind(self.cards.sanitize.toggled, object.properties.sanitize)

        self.binder.bind(
            self.cards.sanitize.controls.preserve_separators.toggled, object.properties.preserve_separators
        )
        self.binder.bind(
            object.properties.preserve_separators, self.cards.sanitize.controls.preserve_separators.setChecked
        )
        self.cards.sanitize.set_options_visible(object.sanitize)

        self.binder.bind(object.properties.add, self.cards.add.setChecked)
        self.binder.bind(self.cards.add.toggled, object.properties.add)

        self.binder.bind(self.cards.add.controls.direction.valueChanged, object.properties.add_direction)
        self.binder.bind(object.properties.add_direction, self.cards.add.controls.direction.setValue)
        self.cards.add.controls.text.bind_property(object.properties.add_text)
        self.cards.add.set_options_visible(object.add)

        self.binder.bind(object.properties.auto_increment, self.cards.auto_increment.setChecked)
        self.binder.bind(self.cards.auto_increment.toggled, object.properties.auto_increment)

        self.binder.bind(object.properties.trim, self.cards.trim.setChecked)
        self.binder.bind(self.cards.trim.toggled, object.properties.trim)

        self.binder.bind(self.cards.trim.controls.direction.valueChanged, object.properties.trim_direction)
        self.binder.bind(object.properties.trim_direction, self.cards.trim.controls.direction.setValue)
        self.cards.trim.controls.max_length.bind_property(object.properties.trim_max_length)
        self.cards.trim.set_options_visible(object.trim)

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
