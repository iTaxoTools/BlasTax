from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card

from ..common.types import BlastMethod
from ..common.view import (
    BatchProgressCard,
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OptionCard,
    OutputDirectorySelector,
    PathDatabaseSelector,
)
from ..common.widgets import (
    BlastMethodCombobox,
    ConsolePropertyLineEdit,
    ElidedLineEdit,
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


class FilterOptionSelector(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("Filter options:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = QtWidgets.QLabel("Set minimum thresholds for taxonomy assignment.")

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
        self.addLayout(options_layout)


class TaxDbCard(OptionCard):
    selectedPath = QtCore.Signal(Path)

    def __init__(self, parent=None):
        super().__init__("Use TaxDB", "Retrieve the organism name corresponding to the taxid for each result.")
        self.draw_config()
        self.roll = VerticalRollAnimation(self)

    def draw_config(self):
        label = QtWidgets.QLabel("TaxDB folder:")
        label.setMinimumWidth(150)

        field = ElidedLineEdit()
        field.textDeleted.connect(self._handle_text_deleted)
        field.setPlaceholderText("Local directory containing taxdb.btd and taxdb.bti")
        field.setReadOnly(True)

        browse = QtWidgets.QPushButton("Browse")
        browse.clicked.connect(self._handle_browse)
        browse.setFixedWidth(120)

        widget = QtWidgets.QWidget()
        widget.roll = VerticalRollAnimation(widget)
        widget.setVisible(False)
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label)
        layout.addWidget(field, 1)
        layout.addWidget(browse)
        layout.setSpacing(16)

        self.controls.field = field
        self.controls.options = widget

        self.addWidget(widget)

    def _handle_text_deleted(self):
        self.selectedPath.emit(Path())

    def _handle_browse(self, *args):
        filename = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self.window(),
            caption=f"{app.config.title} - Browse file",
        )
        if not filename:
            return
        self.selectedPath.emit(Path(filename))

    def _handle_path_changed(self, name: str):
        self.identifierChanged.emit(str(name))

    def set_identifier(self, identifier: str):
        text = identifier or ""
        self.controls.field.setText(text)

    def set_path(self, path: Path):
        text = str(path) if path != Path() else ""
        self.controls.field.setText(text)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = BatchProgressCard(self)
        self.cards.query = BatchQuerySelector("Query sequences", self)
        self.cards.database = PathDatabaseSelector("\u25B6  BLAST database", self)
        self.cards.output = OutputDirectorySelector("\u25C0  Output folder", self)
        self.cards.blast_options = BlastOptionSelector(self)
        self.cards.filter_options = FilterOptionSelector(self)
        self.cards.taxdb = TaxDbCard(self)

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

        self.binder.bind(object.properties.use_taxdb, self.cards.taxdb.setChecked)
        self.binder.bind(self.cards.taxdb.toggled, object.properties.use_taxdb)
        self.binder.bind(self.cards.taxdb.toggled, self.cards.taxdb.controls.options.roll.setAnimatedVisible)

        self.binder.bind(object.properties.blast_taxdb_path, self.cards.taxdb.set_path)
        self.binder.bind(self.cards.taxdb.selectedPath, object.properties.blast_taxdb_path)

        self.cards.blast_options.controls.blast_num_threads.bind_property(object.properties.blast_num_threads)
        self.cards.blast_options.controls.blast_evalue.bind_property(object.properties.blast_evalue)
        self.cards.blast_options.controls.blast_extra_args.bind_property(object.properties.blast_extra_args)

        self.binder.bind(object.properties.match_pident, self.cards.filter_options.controls.pident.setValue)
        self.binder.bind(self.cards.filter_options.controls.pident.valueChangedSafe, object.properties.match_pident)
        self.cards.filter_options.controls.length.bind_property(object.properties.match_length)

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
