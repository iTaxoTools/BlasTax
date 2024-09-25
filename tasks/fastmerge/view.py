from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import RadioButtonGroup

from ..common.view import (
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OptionalCategory,
    PathFileOutSelector,
)
from ..common.widgets import PropertyLineEdit
from . import long_description, pixmap_medium, title
from .types import FormatGroup


class FormatGroupSelector(Card):
    valueChanged = QtCore.Signal(FormatGroup)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.draw_main(text)
        self.draw_options()

    def draw_main(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        all = QtWidgets.QRadioButton(str(FormatGroup.all))
        fasta = QtWidgets.QRadioButton(str(FormatGroup.fasta))
        fastq = QtWidgets.QRadioButton(str(FormatGroup.fastq))

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_value_changed)
        group.add(all, FormatGroup.all)
        group.add(fasta, FormatGroup.fasta)
        group.add(fastq, FormatGroup.fastq)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(all)
        layout.addWidget(fasta)
        layout.addWidget(fastq, 1)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.label = label
        self.controls.all = all
        self.controls.fasta = fasta
        self.controls.fastq = fastq
        self.controls.group = group

    def draw_options(self):
        layout = QtWidgets.QGridLayout()
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setColumnMinimumWidth(0, 150)
        layout.setColumnStretch(1, 1)
        row = 0

        label = QtWidgets.QLabel("Sequence identifier pattern:")
        field = PropertyLineEdit()
        self.controls.pattern_identifier = field
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        row += 1

        label = QtWidgets.QLabel("Sequence motif pattern:")
        field = PropertyLineEdit()
        self.controls.pattern_sequence = field
        layout.addWidget(label, row, 0)
        layout.addWidget(field, row, 1)
        row += 1

        layout.setRowMinimumHeight(row, 12)
        row += 1

        label = QtWidgets.QLabel("The search words should be in double quotes.")
        layout.addWidget(label, row, 0, 1, 2)
        row += 1

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.roll = VerticalRollAnimation(widget)
        self.controls.options = widget
        self.addWidget(widget)

    def _handle_value_changed(self, value: FormatGroup):
        self.valueChanged.emit(value)
        self.set_options_visible(value)

    def set_value(self, value: FormatGroup):
        self.controls.group.setValue(value)

    def set_options_visible(self, value: FormatGroup):
        self.controls.options.roll.setAnimatedVisible(value != FormatGroup.all)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.input = BatchQuerySelector("Input sequences", self)
        self.cards.output = PathFileOutSelector("\u25C0  Output file", self)
        self.cards.group = FormatGroupSelector("File types", self)
        self.cards.compress = OptionalCategory("Compress output", "", self)

        self.cards.input.controls.header.setVisible(False)
        self.cards.input.controls.single_query.roll._visible_target = False
        self.cards.input.controls.batch_query.roll._visible_target = True
        self.cards.input.set_placeholder_text("Sequence files that will be merged together")
        self.cards.output.set_placeholder_text("Final merged sequence file")

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

        self.binder.bind(object.properties.output_path, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_path)

        self.binder.bind(object.properties.format_group, self.cards.group.set_value)
        self.binder.bind(self.cards.group.valueChanged, object.properties.format_group)

        self.cards.input.bind_batch_model(self.binder, object.input_sequences)
        self.cards.group.controls.pattern_identifier.bind_property(object.properties.pattern_identifier)
        self.cards.group.controls.pattern_sequence.bind_property(object.properties.pattern_sequence)

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
