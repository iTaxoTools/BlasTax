from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.bindings import Binder
from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import RadioButtonGroup

from ..common.types import BlastMethod
from ..common.view import BlastTaskView, GraphicTitleCard, PathDatabaseSelector, PathDirectorySelector, PathFileSelector
from ..common.widgets import (
    BasePropertyLineEdit,
    BlastMethodCombobox,
    ElidedLineEdit,
    FloatPropertyLineEdit,
    GrowingListView,
    IntPropertyLineEdit,
)
from . import long_description, pixmap_medium, title
from .model import PathListModel


class BatchQueryHelp(QtWidgets.QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPlaceholderText("Sequences to match against database contents")
        self.setEnabled(False)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
        )

    def sizeHint(self):
        return QtCore.QSize(0, 0)


class QuerySelector(Card):
    batchModeChanged = QtCore.Signal(bool)
    selectedSinglePath = QtCore.Signal(Path)
    requestedAddPaths = QtCore.Signal(list)
    requestedAddFolder = QtCore.Signal(Path)
    requestDelete = QtCore.Signal(list)
    requestClear = QtCore.Signal()

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.binder = Binder()
        self.draw_mode(text)
        self.draw_single("\u25C0", "Query FASTA file")
        self.draw_batch("\u25C0", "Query FASTA files")

    def draw_mode(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        single = QtWidgets.QRadioButton("Single file")
        batch = QtWidgets.QRadioButton("Batch mode")

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_batch_mode_changed)
        group.add(single, False)
        group.add(batch, True)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(single)
        layout.addWidget(batch, 1)
        layout.addSpacing(136)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.label = label
        self.controls.single = single
        self.controls.batch = batch
        self.controls.batch_mode = group

    def draw_single(self, symbol, text):
        label = QtWidgets.QLabel(f"{symbol}  {text}:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        field = ElidedLineEdit()
        field.setPlaceholderText("Sequences to match against database contents")
        field.textDeleted.connect(self._handle_single_path_deleted)
        field.setReadOnly(True)

        browse = QtWidgets.QPushButton("Browse")
        browse.clicked.connect(self._handle_browse)
        browse.setFixedWidth(120)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label)
        layout.addWidget(field, 1)
        layout.addWidget(browse)
        layout.setSpacing(16)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.addWidget(widget)
        widget.roll = VerticalRollAnimation(widget)
        widget.roll._visible_target = True

        self.controls.single_query = widget
        self.controls.single_field = field

    def draw_batch(self, symbol, text):
        label_symbol = QtWidgets.QLabel(symbol)
        label_symbol.setStyleSheet("""font-size: 16px;""")

        label_text = QtWidgets.QLabel(text + ":")
        label_text.setStyleSheet("""font-size: 16px;""")

        label_spacer = QtWidgets.QLabel("")
        label_spacer.setMinimumWidth(150)

        label_total = QtWidgets.QLabel("Total: 0")

        view = GrowingListView()
        view.requestDelete.connect(self.requestDelete)

        help = BatchQueryHelp()

        add_file = QtWidgets.QPushButton("Add files")
        add_folder = QtWidgets.QPushButton("Add folder")
        clear = QtWidgets.QPushButton("Clear")
        clear.setFixedWidth(120)

        add_file.clicked.connect(self._handle_add_paths)
        add_folder.clicked.connect(self._handle_add_folder)
        clear.clicked.connect(self._handle_clear_paths)

        labels = QtWidgets.QGridLayout()
        labels.setHorizontalSpacing(0)
        labels.setVerticalSpacing(16)
        labels.setRowStretch(3, 1)
        labels.addWidget(label_symbol, 0, 0)
        labels.addWidget(label_text, 0, 1)
        labels.addWidget(label_total, 1, 1)
        labels.addWidget(label_spacer, 2, 0, 1, 2)

        buttons = QtWidgets.QVBoxLayout()
        buttons.setSpacing(8)
        buttons.addWidget(add_file)
        buttons.addWidget(add_folder)
        buttons.addWidget(clear)
        buttons.addStretch(1)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addLayout(labels)
        layout.addWidget(view, 1)
        layout.addWidget(help, 1)
        layout.addLayout(buttons)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.addWidget(widget)
        widget.roll = VerticalRollAnimation(widget)

        self.controls.batch_query = widget
        self.controls.batch_view = view
        self.controls.batch_help = help
        self.controls.batch_total = label_total

    def _handle_batch_mode_changed(self, value):
        self.batchModeChanged.emit(value)

    def _handle_single_path_deleted(self):
        self.selectedSinglePath.emit(Path())

    def _handle_browse(self, *args):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=self.window(),
            caption=f"{app.config.title} - Browse file",
        )
        if not filename:
            return
        self.selectedSinglePath.emit(Path(filename))

    def _handle_add_paths(self, *args):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
            parent=self.window(),
            caption=f"{app.config.title} - Browse files",
        )
        paths = [Path(filename) for filename in filenames]
        self.requestedAddPaths.emit(paths)

    def _handle_add_folder(self, *args):
        filename = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self.window(),
            caption=f"{app.config.title} - Browse folder",
        )
        if not filename:
            return
        self.requestedAddFolder.emit(Path(filename))

    def _handle_clear_paths(self):
        self.requestClear.emit()

    def set_batch_mode(self, value: bool):
        self.controls.batch_mode.setValue(value)
        self.controls.batch_query.roll.setAnimatedVisible(value)
        self.controls.single_query.roll.setAnimatedVisible(not value)

    def set_batch_model(self, model: PathListModel):
        self.controls.batch_view.setModel(model)

    def set_batch_total(self, total: int):
        self.controls.batch_total.setText(f"Total: {total}")

    def set_batch_help_visible(self, visible: bool):
        self.controls.batch_help.setVisible(visible)
        self.controls.batch_view.setVisible(not visible)

    def set_path(self, path: Path):
        text = str(path) if path != Path() else ""
        self.controls.single_field.setText(text)


class OptionsSelector(Card):
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
                BlastMethod.blastx,
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


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.query = QuerySelector("Input mode", self)
        self.cards.database = PathDatabaseSelector("\u25C0  BLAST database", self)
        self.cards.options = OptionsSelector(self)
        self.cards.extra = PathFileSelector("\u25C0  Nucleotides file", self)
        self.cards.output = PathDirectorySelector("\u25B6  Output folder", self)

        self.cards.database.set_placeholder_text("Match all query sequences against this database")
        self.cards.extra.set_placeholder_text("Extra FASTA file for blastx parsing")
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
        self.binder.bind(object.reportResults, self.report_results)
        self.binder.bind(object.progression, self.cards.progress.showProgress)

        self.binder.bind(object.properties.name, self.cards.title.setTitle)
        self.binder.bind(object.properties.busy, self.cards.progress.setVisible)

        self.binder.bind(object.properties.batch_mode, self.cards.query.set_batch_mode)
        self.binder.bind(self.cards.query.batchModeChanged, object.properties.batch_mode)

        self.binder.bind(object.properties.input_query_path, self.cards.query.set_path)
        self.binder.bind(self.cards.query.selectedSinglePath, object.properties.input_query_path)

        self.binder.bind(object.properties.input_database_path, self.cards.database.set_path)
        self.binder.bind(self.cards.database.selectedPath, object.properties.input_database_path)

        self.binder.bind(object.properties.input_nucleotides_path, self.cards.extra.set_path)
        self.binder.bind(self.cards.extra.selectedPath, object.properties.input_nucleotides_path)

        self.binder.bind(object.properties.output_path, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_path)

        self.binder.bind(self.cards.query.selectedSinglePath, object.properties.output_path, lambda p: p.parent)

        self.binder.bind(object.properties.blast_method, self.cards.options.controls.blast_method.setValue)
        self.binder.bind(self.cards.options.controls.blast_method.valueChanged, object.properties.blast_method)

        self.binder.bind(self.cards.query.requestClear, object.clear_paths)
        self.binder.bind(self.cards.query.requestDelete, object.delete_paths)
        self.binder.bind(self.cards.query.requestedAddPaths, object.add_paths)
        self.binder.bind(self.cards.query.requestedAddFolder, object.add_folder)

        self.binder.bind(object.properties.input_query_list_total, self.cards.query.set_batch_total)
        self.binder.bind(
            object.properties.input_query_list_rows, self.cards.query.set_batch_help_visible, proxy=lambda x: x == 0
        )

        self.binder.bind(object.input_query_list.rowsInserted, self.cards.query.controls.batch_view.updateGeometry)
        self.binder.bind(object.input_query_list.rowsRemoved, self.cards.query.controls.batch_view.updateGeometry)
        self.binder.bind(object.input_query_list.modelReset, self.cards.query.controls.batch_view.updateGeometry)

        self.binder.bind(
            object.properties.blast_method,
            self.cards.extra.roll_animation.setAnimatedVisible,
            proxy=lambda x: x == BlastMethod.blastx,
        )

        self.cards.options.controls.blast_num_threads.bind_property(object.properties.blast_num_threads)
        self.cards.options.controls.blast_evalue.bind_property(object.properties.blast_evalue)
        self.cards.options.controls.blast_extra_args.bind_property(object.properties.blast_extra_args)

        self.binder.bind(object.properties.editable, self.setEditable)

        self.cards.query.set_batch_model(object.input_query_list)

    def setEditable(self, editable: bool):
        self.cards.query.setEnabled(editable)
        self.cards.database.setEnabled(editable)
        self.cards.options.setEnabled(editable)
        self.cards.extra.setEnabled(editable)
        self.cards.output.setEnabled(editable)

    def open(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=self.window(),
            caption=f"{app.config.title} - Open file",
        )
        if not filename:
            return
        self.object.open(Path(filename))
