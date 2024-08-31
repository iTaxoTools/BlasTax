from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import LongLabel, RadioButtonGroup

from ..common.types import BlastMethod
from ..common.view import (
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OutputDirectorySelector,
    PathDatabaseSelector,
)
from ..common.widgets import (
    BasePropertyLineEdit,
    BlastMethodCombobox,
    FloatPropertyLineEdit,
    IntPropertyLineEdit,
)
from . import long_description, pixmap_medium, title
from .types import DecontVariable


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
        field = BlastMethodCombobox(BlastMethod)
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


class DecontVariableSelector(Card):
    valueChanged = QtCore.Signal(DecontVariable)

    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("Decont. variable:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = LongLabel(
            "The BLAST reported value that will be used for comparisons "
            "between ingroup and outgroup. On a tie, the sequence is preserved."
        )

        buttons = QtWidgets.QHBoxLayout()
        buttons.setContentsMargins(0, 2, 0, 0)
        buttons.setSpacing(32)

        group = RadioButtonGroup()
        for variable in DecontVariable:
            button = QtWidgets.QRadioButton(variable.variable)
            buttons.addWidget(button, 1)
            group.add(button, variable)
            group.valueChanged.connect(self._handle_variable_changed)
        self.controls.variable = group

        layout = QtWidgets.QGridLayout()
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 10)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(16)
        layout.addWidget(label, 0, 0)
        layout.addLayout(buttons, 0, 1)
        layout.addWidget(description, 1, 0, 1, 3)
        self.addLayout(layout)

    def _handle_variable_changed(self, value: DecontVariable):
        self.valueChanged.emit(value)

    def setValue(self, value):
        self.controls.variable.setValue(value)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.query = BatchQuerySelector(self)
        self.cards.ingroup = PathDatabaseSelector("\u25B6  BLAST ingroup", self)
        self.cards.outgroup = PathDatabaseSelector("\u25B6  BLAST outgroup", self)
        self.cards.output = OutputDirectorySelector("\u25C0  Output folder", self)
        self.cards.blast_options = BlastOptionSelector(self)
        self.cards.decont_variable = DecontVariableSelector(self)

        self.cards.query.set_placeholder_text("Sequences to match against database contents (FASTA or FASTQ)")
        self.cards.ingroup.set_placeholder_text("Queries that best match this database will be preserved")
        self.cards.outgroup.set_placeholder_text("Queries that best match this database will be discarded")
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

        self.binder.bind(object.properties.ingroup_database_path, self.cards.ingroup.set_path)
        self.binder.bind(self.cards.ingroup.selectedPath, object.properties.ingroup_database_path)

        self.binder.bind(object.properties.outgroup_database_path, self.cards.outgroup.set_path)
        self.binder.bind(self.cards.outgroup.selectedPath, object.properties.outgroup_database_path)

        self.binder.bind(object.properties.decont_variable, self.cards.decont_variable.setValue)
        self.binder.bind(self.cards.decont_variable.valueChanged, object.properties.decont_variable)

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

        self.binder.bind(object.properties.blast_method, self.cards.blast_options.controls.blast_method.setValue)
        self.binder.bind(self.cards.blast_options.controls.blast_method.valueChanged, object.properties.blast_method)

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
