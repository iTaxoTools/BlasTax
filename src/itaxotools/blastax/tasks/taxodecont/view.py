from PySide6 import QtCore, QtGui, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import RadioButtonGroup

from ..common.types import BlastMethod
from ..common.view import (
    BatchProgressCard,
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OutputDirectorySelector,
    PathDatabaseSelector,
    PathDirectorySelector,
)
from ..common.widgets import (
    BlastMethodCombobox,
    ConsolePropertyLineEdit,
    ElidedLineEdit,
    FloatPropertyLineEdit,
    GrowingTextEdit,
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

        check_pident = QtWidgets.QCheckBox("Identity")
        field_pident = PidentSpinBox()
        desc_pident = QtWidgets.QLabel("Minimum identity percentage (pident)")
        desc_pident.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(check_pident, row, 0)
        options_layout.addWidget(field_pident, row, 1)
        options_layout.addWidget(desc_pident, row, 3)
        self.controls.check_pident = check_pident
        self.controls.threshold_pident = field_pident
        row += 1

        check_bitscore = QtWidgets.QCheckBox("Bitscore")
        field_bitscore = FloatPropertyLineEdit()
        desc_bitscore = QtWidgets.QLabel("Minimum bit score")
        desc_bitscore.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(check_bitscore, row, 0)
        options_layout.addWidget(field_bitscore, row, 1)
        options_layout.addWidget(desc_bitscore, row, 3)
        self.controls.check_bitscore = check_bitscore
        self.controls.threshold_bitscore = field_bitscore
        row += 1

        check_length = QtWidgets.QCheckBox("Length")
        field_length = FloatPropertyLineEdit()
        desc_length = QtWidgets.QLabel("Minimum alignment sequence length")
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


class TaxIdSelector(Card):
    selectedPath = QtCore.Signal(Path)
    modeChanged = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        label = QtWidgets.QLabel("TaxID filter:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        radio_text = QtWidgets.QRadioButton("Enter as text")
        radio_file = QtWidgets.QRadioButton("From file")

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_mode_changed)
        group.add(radio_text, True)
        group.add(radio_file, False)

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(label)
        title_layout.addWidget(radio_text)
        title_layout.addWidget(radio_file)
        title_layout.addStretch(1)
        title_layout.setSpacing(16)

        # Text input widget
        text_edit = GrowingTextEdit()
        text_edit.document().setDocumentMargin(8)
        text_edit.setPlaceholderText("Enter taxon IDs, one per line and/or separated by commas...")
        fixed_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        text_edit.setFont(fixed_font)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.addWidget(text_edit)

        text_widget = QtWidgets.QWidget()
        text_widget.setLayout(text_layout)
        text_widget.roll = VerticalRollAnimation(text_widget)

        # File input widget
        file_field = ElidedLineEdit()
        file_field.textDeleted.connect(self._handle_text_deleted)
        file_field.setPlaceholderText("Text file containing taxon IDs, one per line")
        file_field.setReadOnly(True)

        browse = QtWidgets.QPushButton("Browse")
        browse.clicked.connect(self._handle_browse)
        browse.setFixedWidth(120)

        file_layout = QtWidgets.QHBoxLayout()
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.addWidget(file_field, 1)
        file_layout.addWidget(browse)
        file_layout.setSpacing(16)

        file_widget = QtWidgets.QWidget()
        file_widget.setLayout(file_layout)
        file_widget.roll = VerticalRollAnimation(file_widget)
        file_widget.setVisible(False)

        # Negative mode option
        radio_positive = QtWidgets.QRadioButton(
            "This list defines contaminants that are discarded on match (restrict search to include only the specified taxIDs)."
        )
        radio_negative = QtWidgets.QRadioButton(
            "This list defines non-contaminants which are always kept (restrict search to everything except the specified taxIDs)."
        )
        checkbox_expand = QtWidgets.QCheckBox("Expand the provided taxIDs to include their descendant taxIDs.")

        negative_group = RadioButtonGroup()
        negative_group.add(radio_positive, False)
        negative_group.add(radio_negative, True)

        mode_layout = QtWidgets.QVBoxLayout()
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(8)
        mode_layout.addWidget(radio_positive)
        mode_layout.addWidget(radio_negative)
        mode_layout.addWidget(checkbox_expand)

        self.controls.mode = group
        self.controls.negative = negative_group
        self.controls.expand = checkbox_expand
        self.controls.text_edit = text_edit
        self.controls.text_widget = text_widget
        self.controls.file_field = file_field
        self.controls.file_widget = file_widget

        self.addLayout(title_layout)
        self.addWidget(text_widget)
        self.addWidget(file_widget)
        self.addLayout(mode_layout)

    def _handle_mode_changed(self, value):
        self.controls.text_widget.roll.setAnimatedVisible(value)
        self.controls.file_widget.roll.setAnimatedVisible(not value)
        self.modeChanged.emit(value)

    def _handle_browse(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=self.window(),
            caption=f"{app.config.title} - Browse file",
        )
        if not filename:
            return
        self.selectedPath.emit(Path(filename))

    def _handle_text_deleted(self):
        self.selectedPath.emit(Path())

    def set_path(self, path: Path):
        text = str(path) if path != Path() else ""
        self.controls.file_field.setText(text)

    def set_mode(self, value: bool):
        self.controls.mode.setValue(value)


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
        self.cards.taxdb = PathDirectorySelector("TaxDB folder", "in", self)
        self.cards.output = OutputDirectorySelector("Output folder", self)
        self.cards.blast_options = BlastOptionSelector(self)
        self.cards.decont_options = DecontOptionSelector(self)
        self.cards.taxid = TaxIdSelector(self)

        self.cards.query.set_placeholder_text("Sequences to match against database contents (FASTA or FASTQ)")
        self.cards.database.set_placeholder_text("Match all query sequences against this database")
        self.cards.taxdb.set_placeholder_text("Directory containing taxonomy4blast.sqlite3 (required by taxID filter)")

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

        self.binder.bind(object.properties.blast_taxdb_path, self.cards.taxdb.set_path)
        self.binder.bind(self.cards.taxdb.selectedPath, object.properties.blast_taxdb_path)

        self.binder.bind(object.properties.filter_pident, self.cards.decont_options.controls.check_pident.setChecked)
        self.binder.bind(self.cards.decont_options.controls.check_pident.toggled, object.properties.filter_pident)
        self.binder.bind(
            object.properties.threshold_pident, self.cards.decont_options.controls.threshold_pident.setValue
        )
        self.binder.bind(
            self.cards.decont_options.controls.threshold_pident.valueChangedSafe, object.properties.threshold_pident
        )

        self.binder.bind(
            object.properties.filter_bitscore, self.cards.decont_options.controls.check_bitscore.setChecked
        )
        self.binder.bind(self.cards.decont_options.controls.check_bitscore.toggled, object.properties.filter_bitscore)
        self.cards.decont_options.controls.threshold_bitscore.bind_property(object.properties.threshold_bitscore)

        self.binder.bind(object.properties.filter_length, self.cards.decont_options.controls.check_length.setChecked)
        self.binder.bind(self.cards.decont_options.controls.check_length.toggled, object.properties.filter_length)
        self.cards.decont_options.controls.threshold_length.bind_property(object.properties.threshold_length)

        self.binder.bind(object.properties.taxid_mode_text, self.cards.taxid.set_mode)
        self.binder.bind(self.cards.taxid.modeChanged, object.properties.taxid_mode_text)

        self.binder.bind(object.properties.taxid_list, self.cards.taxid.controls.text_edit.setText)
        self.binder.bind(self.cards.taxid.controls.text_edit.textEditedSafe, object.properties.taxid_list)

        self.binder.bind(object.properties.taxid_path, self.cards.taxid.set_path)
        self.binder.bind(self.cards.taxid.selectedPath, object.properties.taxid_path)

        self.binder.bind(object.properties.taxid_negative, self.cards.taxid.controls.negative.setValue)
        self.binder.bind(self.cards.taxid.controls.negative.valueChanged, object.properties.taxid_negative)

        self.binder.bind(object.properties.taxid_expand, self.cards.taxid.controls.expand.setChecked)
        self.binder.bind(self.cards.taxid.controls.expand.toggled, object.properties.taxid_expand)

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
