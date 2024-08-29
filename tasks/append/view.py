from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import RadioButtonGroup, RichRadioButton

from ..common.types import BlastMethod
from ..common.view import (
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OptionalCategory,
    PathDatabaseSelector,
    PathDirectorySelector,
)
from ..common.widgets import (
    BasePropertyLineEdit,
    BlastMethodCombobox,
    FloatPropertyLineEdit,
    IntPropertyLineEdit,
    PidentSpinBox,
)
from . import long_description, pixmap_medium, title


class BlastOptionsSelector(Card):
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
        field = BlastMethodCombobox(
            [
                BlastMethod.blastn,
                BlastMethod.blastp,
                BlastMethod.tblastx,
            ]
        )
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


class SequenceSelectionOptions(Card):
    mode_changed = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("Sequence selection:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = QtWidgets.QLabel("Determine how matching sequences are retrieved from the database.")

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(label)
        title_layout.addWidget(description, 1)
        title_layout.setSpacing(16)

        mode_layout = QtWidgets.QVBoxLayout()
        mode_layout.setContentsMargins(12, 0, 0, 0)
        mode_layout.setSpacing(8)

        single = RichRadioButton(
            "Single best match,", "matching the longest query sequence with the best identity percentage"
        )
        multiple = RichRadioButton("Multiple matches,", "fulfilling the criteria of length and identity set below")

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_mode_changed)
        group.add(single, False)
        group.add(multiple, True)
        self.controls.multiple = group

        mode_layout.addWidget(single)
        mode_layout.addWidget(multiple)

        options_layout = QtWidgets.QGridLayout()
        options_layout.setColumnMinimumWidth(0, 16)
        options_layout.setColumnMinimumWidth(1, 54)
        options_layout.setColumnStretch(3, 1)
        options_layout.setHorizontalSpacing(32)
        options_layout.setVerticalSpacing(8)
        row = 0

        name = QtWidgets.QLabel("Length:")
        field = IntPropertyLineEdit()
        description = QtWidgets.QLabel("Minimum alignment sequence length")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 3)
        self.controls.length = field
        row += 1

        name = QtWidgets.QLabel("Identity:")
        field = PidentSpinBox()
        description = QtWidgets.QLabel("Minimum identity percentage (pident)")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 3)
        self.controls.pident = field
        row += 1

        self.addLayout(title_layout)
        self.addLayout(mode_layout)
        self.addLayout(options_layout)

    def _handle_mode_changed(self, value: bool):
        self.mode_changed.emit(value)

    def set_mode(self, value: bool):
        self.controls.mode.setValue(value)

    def set_options_enabled(self, value: bool):
        self.controls.length.setEnabled(value)
        self.controls.pident.setEnabled(value)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.query = BatchQuerySelector("Input mode", self)
        self.cards.database = PathDatabaseSelector("\u25C0  BLAST database", self)
        self.cards.blast_options = BlastOptionsSelector(self)
        self.cards.append_options = SequenceSelectionOptions(self)
        self.cards.output = PathDirectorySelector("\u25B6  Output folder", self)
        self.cards.timestamp = OptionalCategory("Append timestamp to output filenames", "", self)

        self.cards.database.set_placeholder_text("Match all query sequences against this database")
        self.cards.output.set_placeholder_text("All output files will be saved here")

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

        self.cards.query.bind_batch_model(self.binder, object.input_queries)

        self.binder.bind(object.properties.input_database_path, self.cards.database.set_path)
        self.binder.bind(self.cards.database.selectedPath, object.properties.input_database_path)

        self.binder.bind(object.properties.output_path, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_path)

        self.binder.bind(object.properties.append_timestamp, self.cards.timestamp.setChecked)
        self.binder.bind(self.cards.timestamp.toggled, object.properties.append_timestamp)

        self.binder.bind(object.properties.blast_method, self.cards.blast_options.controls.blast_method.setValue)
        self.binder.bind(self.cards.blast_options.controls.blast_method.valueChanged, object.properties.blast_method)

        self.cards.blast_options.controls.blast_num_threads.bind_property(object.properties.blast_num_threads)
        self.cards.blast_options.controls.blast_evalue.bind_property(object.properties.blast_evalue)
        self.cards.blast_options.controls.blast_extra_args.bind_property(object.properties.blast_extra_args)

        self.binder.bind(object.properties.append_multiple, self.cards.append_options.controls.multiple.setValue)
        self.binder.bind(self.cards.append_options.controls.multiple.valueChanged, object.properties.append_multiple)
        self.binder.bind(object.properties.append_pident, self.cards.append_options.controls.pident.setValue)
        self.binder.bind(self.cards.append_options.controls.pident.valueChangedSafe, object.properties.append_pident)
        self.cards.append_options.controls.length.bind_property(object.properties.append_length)

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
