from PySide6 import QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.view.cards import Card

from ..common.types import BlastMethod
from ..common.view import (
    BatchProgressCard,
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OutputDirectorySelector,
    PathDatabaseSelector,
)
from ..common.widgets import (
    BlastMethodCombobox,
    ConsolePropertyLineEdit,
    FloatPropertyLineEdit,
    IntPropertyLineEdit,
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
        field = ConsolePropertyLineEdit()
        field.setReadOnly(True)
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_long_layout.addWidget(name, row, 1)
        options_long_layout.addWidget(field, row, 2)
        self.controls.blast_extra_args = field
        row += 1

        self.addLayout(title_layout)
        self.addLayout(options_layout)
        self.addLayout(options_long_layout)


class DecontOptionSelector(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel("Decont. variables:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = QtWidgets.QLabel("Matches above all enabled threshold are considered contaminants.")

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(label)
        title_layout.addWidget(description, 1)
        title_layout.setSpacing(16)

        options_layout = QtWidgets.QGridLayout()
        options_layout.setColumnMinimumWidth(0, 86)
        options_layout.setColumnMinimumWidth(2, 16)
        options_layout.setColumnStretch(3, 1)
        options_layout.setHorizontalSpacing(16)
        options_layout.setVerticalSpacing(8)
        row = 0

        check_pident = QtWidgets.QCheckBox("pident")
        field_pident = FloatPropertyLineEdit()
        desc_pident = QtWidgets.QLabel("Percentage of identical matches")
        desc_pident.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(check_pident, row, 0)
        options_layout.addWidget(field_pident, row, 1)
        options_layout.addWidget(desc_pident, row, 3)
        self.controls.check_pident = check_pident
        self.controls.threshold_pident = field_pident
        row += 1

        check_bitscore = QtWidgets.QCheckBox("bitscore")
        field_bitscore = FloatPropertyLineEdit()
        desc_bitscore = QtWidgets.QLabel("Bit score threshold")
        desc_bitscore.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(check_bitscore, row, 0)
        options_layout.addWidget(field_bitscore, row, 1)
        options_layout.addWidget(desc_bitscore, row, 3)
        self.controls.check_bitscore = check_bitscore
        self.controls.threshold_bitscore = field_bitscore
        row += 1

        check_length = QtWidgets.QCheckBox("length")
        field_length = FloatPropertyLineEdit()
        desc_length = QtWidgets.QLabel("Alignment length threshold")
        desc_length.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(check_length, row, 0)
        options_layout.addWidget(field_length, row, 1)
        options_layout.addWidget(desc_length, row, 3)
        self.controls.check_length = check_length
        self.controls.threshold_length = field_length
        row += 1

        check_pident.toggled.connect(field_pident.setEnabled)
        check_bitscore.toggled.connect(field_bitscore.setEnabled)
        check_length.toggled.connect(field_length.setEnabled)

        field_bitscore.setEnabled(False)
        field_length.setEnabled(False)

        self.addLayout(title_layout)
        self.addLayout(options_layout)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = BatchProgressCard(self)
        self.cards.query = BatchQuerySelector("Query sequences", self)
        self.cards.database = PathDatabaseSelector("BLAST database", "in", self)
        self.cards.output = OutputDirectorySelector("Output folder", self)
        self.cards.blast_options = BlastOptionSelector(self)
        self.cards.decont_options = DecontOptionSelector(self)

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

        self.binder.bind(object.properties.busy, self.cards.progress.setVisible)

        self.cards.query.bind_batch_model(self.binder, object.input_queries)

        self.binder.bind(object.properties.input_database_path, self.cards.database.set_path)
        self.binder.bind(self.cards.database.selectedPath, object.properties.input_database_path)

        self.binder.bind(object.properties.filter_pident, self.cards.decont_options.controls.check_pident.setChecked)
        self.binder.bind(self.cards.decont_options.controls.check_pident.toggled, object.properties.filter_pident)
        self.cards.decont_options.controls.threshold_pident.bind_property(object.properties.threshold_pident)

        self.binder.bind(
            object.properties.filter_bitscore, self.cards.decont_options.controls.check_bitscore.setChecked
        )
        self.binder.bind(self.cards.decont_options.controls.check_bitscore.toggled, object.properties.filter_bitscore)
        self.cards.decont_options.controls.threshold_bitscore.bind_property(object.properties.threshold_bitscore)

        self.binder.bind(object.properties.filter_length, self.cards.decont_options.controls.check_length.setChecked)
        self.binder.bind(self.cards.decont_options.controls.check_length.toggled, object.properties.filter_length)
        self.cards.decont_options.controls.threshold_length.bind_property(object.properties.threshold_length)

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
