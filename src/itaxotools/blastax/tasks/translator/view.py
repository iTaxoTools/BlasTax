from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import GLineEdit, NoWheelComboBox, RadioButtonGroup, RichRadioButton

from ..common.view import (
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OptionCard,
    PathDirectorySelector,
)
from . import long_description, pixmap_medium, title
from .types import CODON_TABLES, READING_FRAMES, TranslationMode


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

        options_widget = QtWidgets.QWidget()
        options_widget.roll = VerticalRollAnimation(options_widget)
        options_layout = QtWidgets.QVBoxLayout(options_widget)
        options_layout.setContentsMargins(0, 0, 0, 0)
        nucleotides = QtWidgets.QCheckBox("Additionally write nucleotide sequences of the ORF in separate file.")
        options_layout.addWidget(nucleotides)

        self.controls.mode = group
        self.controls.nucleotides = nucleotides
        self.controls.options = options_widget

        self.addWidget(title)
        self.addLayout(mode_layout)
        self.addWidget(options_widget)

    def _handle_mode_changed(self, mode: TranslationMode):
        self.mode_changed.emit(mode)

    def set_mode(self, mode: TranslationMode):
        self.controls.mode.setValue(mode)

    def set_options_visible(self, value: bool):
        self.controls.options.roll.setAnimatedVisible(value)


class CodonTableSelector(Card):
    code_changed = QtCore.Signal(int)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.draw_main(text)

    def draw_main(self, text):
        title = QtWidgets.QLabel(text + ":")
        title.setStyleSheet("""font-size: 16px;""")
        title.setMinimumWidth(150)

        combo = NoWheelComboBox()
        for id, name in CODON_TABLES.items():
            label = f"{(str(id) + ':').rjust(3)}  {name}"
            combo.addItem(label, id)
        combo.currentIndexChanged.connect(self._handle_index_changed)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(combo, 1)

        self.controls.combo = combo

        self.addLayout(layout)

    def _handle_index_changed(self, index: int):
        code = self.controls.combo.itemData(index)
        self.code_changed.emit(code)

    def set_code(self, code: int):
        index = self.controls.combo.findData(code)
        index = self.controls.combo.setCurrentIndex(index)


class ReadingFrameSelector(Card):
    frame_changed = QtCore.Signal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.draw_main(text)

    def draw_main(self, text):
        title = QtWidgets.QLabel(text + ":")
        title.setStyleSheet("""font-size: 16px;""")
        title.setMinimumWidth(150)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(16)
        layout.addWidget(title)

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_frame_changed)
        for key, label in READING_FRAMES.items():
            button = QtWidgets.QRadioButton(label)
            layout.addWidget(button)
            layout.addSpacing(8)
            group.add(button, key)

        layout.addStretch(1)

        self.controls.group = group

        self.addLayout(layout)

    def _handle_frame_changed(self, frame: str):
        self.frame_changed.emit(frame)

    def set_frame(self, frame: str):
        self.controls.group.setValue(frame)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.input = BatchQuerySelector("Input sequences", self)
        self.cards.output = PathDirectorySelector("Output folder", "out", self)
        self.cards.output_filename = FilenameSelector("Output filename", self)
        self.cards.mode = ModeSelector("Translation mode", self)
        self.cards.code = CodonTableSelector("Codon table", self)
        self.cards.frame = ReadingFrameSelector("Reading frame", self)
        self.cards.log = OptionCard(
            "Write logfile:", "Generate a logfile with warnings and information about special cases.", self
        )

        self.cards.input.set_placeholder_text("Sequences that will be translated")
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

        self.cards.input.bind_batch_model(self.binder, object.input_paths)

        self.binder.bind(object.properties.output_path, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_path)

        self.binder.bind(object.properties.output_filename, self.cards.output_filename.set_name)
        self.binder.bind(self.cards.output_filename.nameChanged, object.properties.output_filename)
        self.binder.bind(
            object.input_paths.properties.batch_mode,
            self.cards.output_filename.roll_animation.setAnimatedVisible,
            lambda x: not x,
        )

        self.binder.bind(object.properties.option_mode, self.cards.mode.set_mode)
        self.binder.bind(self.cards.mode.mode_changed, object.properties.option_mode)

        self.binder.bind(object.properties.option_code, self.cards.code.set_code)
        self.binder.bind(self.cards.code.code_changed, object.properties.option_code)

        self.binder.bind(object.properties.option_frame, self.cards.frame.set_frame)
        self.binder.bind(self.cards.frame.frame_changed, object.properties.option_frame)

        self.binder.bind(object.properties.option_log, self.cards.log.setChecked)
        self.binder.bind(self.cards.log.toggled, object.properties.option_log)

        self.binder.bind(
            object.properties.option_mode,
            self.cards.mode.set_options_visible,
            proxy=lambda mode: bool(mode == TranslationMode.transcript),
        )
        self.binder.bind(object.properties.option_nucleotides, self.cards.mode.controls.nucleotides.setChecked)
        self.binder.bind(self.cards.mode.controls.nucleotides.toggled, object.properties.option_nucleotides)

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
