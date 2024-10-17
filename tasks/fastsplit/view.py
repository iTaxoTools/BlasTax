from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import GLineEdit, RadioButtonGroup

from ..common.view import (
    BlastTaskView,
    GraphicTitleCard,
    OptionCard,
    PathDirectorySelector,
    PathFileSelector,
)
from ..common.widgets import IntPropertyLineEdit, PropertyLineEdit
from . import long_description, pixmap_medium, title
from .types import FileFormat, SplitOption


class TemplateSelector(Card):
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


class FileFormatSelector(Card):
    valueChanged = QtCore.Signal(FileFormat)
    optionChanged = QtCore.Signal(SplitOption)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.draw_main(text)
        self.draw_options()

    def draw_main(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        fasta = QtWidgets.QRadioButton(str(FileFormat.fasta))
        fastq = QtWidgets.QRadioButton(str(FileFormat.fastq))
        text = QtWidgets.QRadioButton(str(FileFormat.text))

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_value_changed)
        group.add(fasta, FileFormat.fasta)
        group.add(fastq, FileFormat.fastq)
        group.add(text, FileFormat.text)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(fasta)
        layout.addWidget(fastq)
        layout.addWidget(text, 1)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.label = label
        self.controls.fasta = fasta
        self.controls.fastq = fastq
        self.controls.text = text
        self.controls.group = group

    def draw_options(self):
        layout = QtWidgets.QGridLayout()
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setColumnMinimumWidth(0, 150)
        layout.setColumnStretch(1, 1)
        row = 0

        group = RadioButtonGroup()
        self.controls.option_group = group
        group.valueChanged.connect(self._handle_option_changed)

        option = SplitOption.max_size
        radio = QtWidgets.QRadioButton(str(option))
        group.add(radio, option)
        field = PropertyLineEdit()
        self.controls.max_size = field
        layout.addWidget(radio, row, 0)
        layout.addWidget(field, row, 1)
        row += 1

        option = SplitOption.split_n
        radio = QtWidgets.QRadioButton(str(option))
        group.add(radio, option)
        field = IntPropertyLineEdit()
        self.controls.split_n = field
        layout.addWidget(radio, row, 0)
        layout.addWidget(field, row, 1)
        row += 1

        option = SplitOption.pattern_identifier
        radio = QtWidgets.QRadioButton(str(option))
        group.add(radio, option)
        field = PropertyLineEdit()
        self.controls.pattern_identifier_radio = radio
        self.controls.pattern_identifier = field
        layout.addWidget(radio, row, 0)
        layout.addWidget(field, row, 1)
        row += 1

        option = SplitOption.pattern_sequence
        radio = QtWidgets.QRadioButton(str(option))
        group.add(radio, option)
        field = PropertyLineEdit()
        self.controls.pattern_sequence_radio = radio
        self.controls.pattern_sequence = field
        layout.addWidget(radio, row, 0)
        layout.addWidget(field, row, 1)
        row += 1

        layout.setRowMinimumHeight(row, 12)
        row += 1

        label = QtWidgets.QLabel("The search words for patterns should be in double quotes.")
        layout.addWidget(label, row, 0, 1, 2)
        row += 1

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.roll = VerticalRollAnimation(widget)
        self.controls.options = widget
        self.addWidget(widget)

    def _handle_value_changed(self, value: FileFormat):
        self.valueChanged.emit(value)

    def _handle_option_changed(self, value: SplitOption):
        self.optionChanged.emit(value)

    def set_value(self, value: FileFormat):
        self.controls.group.setValue(value)

    def set_option(self, value: SplitOption):
        self.controls.option_group.setValue(value)

    def set_pattern_available(self, value: bool):
        self.controls.pattern_identifier_radio.setEnabled(value)
        self.controls.pattern_identifier.setEnabled(value)
        self.controls.pattern_sequence_radio.setEnabled(value)
        self.controls.pattern_sequence.setEnabled(value)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.input = PathFileSelector("\u25C0  Input file", self)
        self.cards.output = PathDirectorySelector("\u25C0  Output file", self)
        self.cards.template = TemplateSelector("Filename template", self)
        self.cards.format = FileFormatSelector("Output format", self)
        self.cards.compress = OptionCard("Compress output", "", self)

        self.cards.input.set_placeholder_text("Sequence file that will be split")
        self.cards.output.set_placeholder_text("Folder that will contain all output files")
        self.cards.template.set_placeholder_text('Output files will be named by replacing the hash ("#") with a number')

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

        self.binder.bind(object.properties.filename_template, self.cards.template.set_name)
        self.binder.bind(self.cards.template.nameChanged, object.properties.filename_template)

        self.binder.bind(object.properties.output_format, self.cards.format.set_value)
        self.binder.bind(self.cards.format.valueChanged, object.properties.output_format)
        self.binder.bind(object.properties.split_option, self.cards.format.set_option)
        self.binder.bind(self.cards.format.optionChanged, object.properties.split_option)
        self.binder.bind(object.properties.pattern_available, self.cards.format.set_pattern_available)

        self.binder.bind(object.properties.compress, self.cards.compress.setChecked)
        self.binder.bind(self.cards.compress.toggled, object.properties.compress)

        self.cards.format.controls.max_size.bind_property(object.properties.max_size)
        self.cards.format.controls.split_n.bind_property(object.properties.split_n)
        self.cards.format.controls.pattern_identifier.bind_property(object.properties.pattern_identifier)
        self.cards.format.controls.pattern_sequence.bind_property(object.properties.pattern_sequence)

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
