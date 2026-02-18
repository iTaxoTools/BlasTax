from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import RadioButtonGroup, RichRadioButton

from ..common.view import (
    BatchProgressCard,
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OutputDirectorySelector,
)
from . import long_description, pixmap_medium, title
from .types import AdjustDirection, AlignmentStrategy


class StrategySelector(Card):
    option_changed = QtCore.Signal(AlignmentStrategy)

    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("Alignment strategy:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        radio_layout = QtWidgets.QVBoxLayout()
        radio_layout.setContentsMargins(12, 0, 0, 0)
        radio_layout.setSpacing(8)

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_option_changed)
        self.controls.group = group

        for option in AlignmentStrategy:
            button = RichRadioButton(f"{option.title}:", f"{option.description}.")
            group.add(button, option)
            radio_layout.addWidget(button)

        self.addWidget(label)
        self.addLayout(radio_layout)

    def _handle_option_changed(self, value: AlignmentStrategy):
        self.option_changed.emit(value)

    def set_option(self, value: AlignmentStrategy):
        self.controls.group.setValue(value)


class AdjustDirectionSelector(Card):
    option_changed = QtCore.Signal(AdjustDirection)

    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("Adjust direction:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        layout.addWidget(label)

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_option_changed)
        self.controls.group = group

        for option in AdjustDirection:
            button = QtWidgets.QRadioButton(option.title)
            group.add(button, option)
            layout.addWidget(button, 1)
            layout.addSpacing(16)

        layout.addStretch(6)

        self.addLayout(layout)

    def _handle_option_changed(self, value: AdjustDirection):
        self.option_changed.emit(value)

    def set_option(self, value: AdjustDirection):
        self.controls.group.setValue(value)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = BatchProgressCard(self)
        self.cards.query = BatchQuerySelector("Input sequences", self)
        self.cards.output = OutputDirectorySelector("Output folder", self)
        self.cards.strategy = StrategySelector(self)
        self.cards.adjust_direction = AdjustDirectionSelector(self)

        self.cards.query.set_placeholder_text("FASTA sequences for alignment")

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

        self.binder.bind(
            object.properties.append_configuration, self.cards.output.controls.append_configuration.setChecked
        )
        self.binder.bind(
            self.cards.output.controls.append_configuration.toggled, object.properties.append_configuration
        )

        self.binder.bind(object.properties.append_timestamp, self.cards.output.controls.append_timestamp.setChecked)
        self.binder.bind(self.cards.output.controls.append_timestamp.toggled, object.properties.append_timestamp)

        self.binder.bind(object.properties.strategy, self.cards.strategy.set_option)
        self.binder.bind(self.cards.strategy.option_changed, object.properties.strategy)

        self.binder.bind(object.properties.adjust_direction, self.cards.adjust_direction.set_option)
        self.binder.bind(self.cards.adjust_direction.option_changed, object.properties.adjust_direction)

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
