from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import LongLabel, RadioButtonGroup, RichRadioButton

from ..common.types import BlastMethod
from ..common.view import (
    BlastTaskView,
    GraphicTitleCard,
    OutputDirectorySelector,
    PathDatabaseSelector,
    PathFileSelector,
)
from ..common.widgets import (
    BasePropertyLineEdit,
    BlastMethodCombobox,
    FloatPropertyLineEdit,
    IntPropertyLineEdit,
    PidentSpinBox,
)
from . import long_description, pixmap_medium, title


class BlastOptionSelector(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("BLAST options:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = QtWidgets.QLabel("Parametrize the method and arguments passed to the BLAST+ executables.")

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(label)
        title_layout.addWidget(description, 1)
        title_layout.setSpacing(16)

        options_layout = QtWidgets.QGridLayout()
        options_layout.setColumnMinimumWidth(0, 16)
        options_layout.setColumnMinimumWidth(1, 54)
        options_layout.setColumnStretch(3, 1)
        options_layout.setHorizontalSpacing(32)
        options_layout.setVerticalSpacing(8)
        row = 0

        name = QtWidgets.QLabel("Method:")
        field = BlastMethodCombobox([BlastMethod.blastn])
        description = QtWidgets.QLabel("Comparison type between query and database")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 3)
        self.controls.blast_method = field
        row += 1

        name = QtWidgets.QLabel("E-value:")
        field = FloatPropertyLineEdit()
        description = QtWidgets.QLabel("Expectation value threshold for saving hits")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 3)
        self.controls.blast_evalue = field
        row += 1

        name = QtWidgets.QLabel("Threads:")
        field = IntPropertyLineEdit()
        description = QtWidgets.QLabel("Number of threads (CPUs) to use in the BLAST search")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 3)
        self.controls.blast_num_threads = field
        row += 1

        options_long_layout = QtWidgets.QGridLayout()
        options_long_layout.setContentsMargins(0, 0, 0, 0)
        options_long_layout.setColumnMinimumWidth(0, 16)
        options_long_layout.setColumnMinimumWidth(1, 54)
        options_long_layout.setColumnStretch(2, 1)
        options_long_layout.setHorizontalSpacing(32)
        options_long_layout.setVerticalSpacing(8)
        row = 0

        name = QtWidgets.QLabel("Locked:")
        field = BasePropertyLineEdit()
        field.setReadOnly(True)
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_long_layout.addWidget(name, row, 1)
        options_long_layout.addWidget(field, row, 2)
        self.controls.blast_extra_args = field
        row += 1

        self.addLayout(title_layout)
        self.addLayout(options_layout)
        self.addLayout(options_long_layout)


class IdentityThresholdCard(Card):
    valueChanged = QtCore.Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        label = QtWidgets.QLabel("Identity threshold")
        label.setStyleSheet("""font-size: 16px;""")

        field = PidentSpinBox()

        field.valueChangedSafe.connect(self.valueChanged)

        description = LongLabel(
            "BLAST matches with a percentage of identical matches (pident) above the given value "
            "will be considered similar and included in the output FASTA file."
        )

        layout = QtWidgets.QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(field, 0, 1)
        layout.addWidget(description, 1, 0)
        layout.setColumnStretch(0, 1)
        layout.setHorizontalSpacing(32)
        layout.setVerticalSpacing(12)
        self.addLayout(layout)

        self.controls.field = field

    def setValue(self, value: float):
        self.controls.field.setValue(value)


class RetrievalOptionSelector(Card):
    mode_changed = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("Sequence retrieval:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = QtWidgets.QLabel("Determine which sequences are retrieved on a match.")

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(label)
        title_layout.addWidget(description, 1)
        title_layout.setSpacing(16)

        mode_layout = QtWidgets.QVBoxLayout()
        mode_layout.setContentsMargins(12, 0, 0, 0)
        mode_layout.setSpacing(8)

        alignment = RichRadioButton("Alignment,", "the aligned parts of the reads as detected by BLAST")
        original = RichRadioButton("Original reads,", "the full sequences from the query fasta file")

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_mode_changed)
        group.add(alignment, False)
        group.add(original, True)
        self.controls.mode = group

        mode_layout.addWidget(alignment)
        mode_layout.addWidget(original)

        self.addLayout(title_layout)
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
        self.cards.query = PathFileSelector("\u25B6  Query sequences", self)
        self.cards.database = PathDatabaseSelector("\u25B6  BLAST database", self)
        self.cards.output = OutputDirectorySelector("\u25C0  Output folder", self)
        self.cards.blast_options = BlastOptionSelector(self)
        self.cards.pident_threshold = IdentityThresholdCard(self)
        self.cards.retrieval = RetrievalOptionSelector()

        self.cards.query.set_placeholder_text("Sequences to match against database contents (FASTA or FASTQ)")
        self.cards.database.set_placeholder_text("Match all query sequences against this database")

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

        self.binder.bind(object.properties.input_query_path, self.cards.query.set_path)
        self.binder.bind(self.cards.query.selectedPath, object.properties.input_query_path)

        self.binder.bind(object.properties.input_database_path, self.cards.database.set_path)
        self.binder.bind(self.cards.database.selectedPath, object.properties.input_database_path)

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

        self.binder.bind(self.cards.query.selectedPath, object.properties.output_path, lambda p: p.parent)

        self.binder.bind(object.properties.blast_method, self.cards.blast_options.controls.blast_method.setValue)
        self.binder.bind(self.cards.blast_options.controls.blast_method.valueChanged, object.properties.blast_method)

        self.binder.bind(object.properties.retrieve_original, self.cards.retrieval.set_mode)
        self.binder.bind(self.cards.retrieval.mode_changed, object.properties.retrieve_original)

        self.binder.bind(object.properties.pident_threshold, self.cards.pident_threshold.setValue)
        self.binder.bind(self.cards.pident_threshold.valueChanged, object.properties.pident_threshold)

        self.cards.blast_options.controls.blast_num_threads.bind_property(object.properties.blast_num_threads)
        self.cards.blast_options.controls.blast_evalue.bind_property(object.properties.blast_evalue)
        self.cards.blast_options.controls.blast_extra_args.bind_property(object.properties.blast_extra_args)

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
