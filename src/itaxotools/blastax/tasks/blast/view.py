from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import LongLabel

from ..common.types import BLAST_OUTFMT_SPECIFIERS_TABULAR
from ..common.view import (
    BlastTaskView,
    GraphicTitleCard,
    OutputDirectorySelector,
    PathDatabaseSelector,
    PathFileSelector,
)
from ..common.widgets import (
    BlastMethodCombobox,
    BlastOutfmtFullCombobox,
    ConsolePropertyLineEdit,
    FloatPropertyLineEdit,
    IntPropertyLineEdit,
    PropertyLineEdit,
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
        field = BlastMethodCombobox()
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

        name = QtWidgets.QLabel("Extras:")
        field = ConsolePropertyLineEdit()
        field.setPlaceholderText("Extra arguments to pass to the BLAST+ executable")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_long_layout.addWidget(name, row, 1)
        options_long_layout.addWidget(field, row, 2)
        self.controls.blast_extra_args = field
        row += 1

        options_long_widget = QtWidgets.QWidget()
        options_long_widget.setLayout(options_long_layout)

        self.addLayout(title_layout)
        self.addLayout(options_layout)
        self.addWidget(options_long_widget)

    def set_outfmt_options_visible(self, value: bool):
        self.controls.blast_outfmt_options.setVisible(value)
        self.controls.blast_outfmt_options_label.setVisible(value)


class HelpDialog(QtWidgets.QDialog):
    restore_defaults = QtCore.Signal()
    add_specifier = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{app.config.title} - Format specifiers")
        self.resize(480, 640)

        description = LongLabel(
            "For tabular and comma separated output formats, you may specify "
            "what columns are written in the output file by using "
            "space delimited format specifiers. "
            "All available options are listed below. "
            "Double-click a specifier to add it to the list. "
        )

        table = QtWidgets.QTableWidget()
        table.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Specifier", "Description"])
        table.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignLeft)
        table.horizontalHeaderItem(1).setTextAlignment(QtCore.Qt.AlignLeft)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet(
            """
            QHeaderView::section {
                padding: 4px;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """
        )

        table.setRowCount(len(BLAST_OUTFMT_SPECIFIERS_TABULAR))
        for row, (key, value) in enumerate(BLAST_OUTFMT_SPECIFIERS_TABULAR.items()):
            item_key = QtWidgets.QTableWidgetItem(key)
            item_key.setFlags(item_key.flags() & ~QtCore.Qt.ItemIsEditable)
            table.setItem(row, 0, item_key)

            item_value = QtWidgets.QTableWidgetItem(value)
            item_value.setFlags(item_value.flags() & ~QtCore.Qt.ItemIsEditable)
            table.setItem(row, 1, item_value)
        table.resizeColumnsToContents()

        table.cellDoubleClicked.connect(self._on_cell_double_clicked)

        defaults = QtWidgets.QPushButton("Restore defaults")
        close = QtWidgets.QPushButton("Close")
        close.setAutoDefault(True)
        close.setDefault(True)

        defaults.clicked.connect(self.restore_defaults)
        close.clicked.connect(self.accept)

        layout = QtWidgets.QGridLayout(self)
        layout.setRowMinimumHeight(1, 8)
        layout.setRowMinimumHeight(3, 8)
        layout.setSpacing(8)
        layout.addWidget(description, 0, 0, 1, 3)
        layout.addWidget(table, 2, 0, 1, 3)
        layout.addWidget(defaults, 4, 0, 1, 1)
        layout.addWidget(close, 4, 2, 1, 1)

        self.table = table

    def _on_cell_double_clicked(self, row, column):
        specifier = self.table.item(row, 0).text()
        self.add_specifier.emit(specifier)


class FormatOptionsSelector(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.help_dialog = HelpDialog(self.window())

        label = QtWidgets.QLabel("BLAST output format:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = QtWidgets.QLabel("Alignment view options (outfmt)")
        description.setStyleSheet("QLabel {padding-top: 3px;}")

        outfmt = BlastOutfmtFullCombobox()
        self.controls.outfmt = outfmt

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(label)
        title_layout.addWidget(description, 1)
        title_layout.addWidget(outfmt)
        title_layout.setSpacing(16)

        options_layout = QtWidgets.QGridLayout()
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setColumnMinimumWidth(1, 120)
        options_layout.setColumnStretch(0, 1)
        options_layout.setHorizontalSpacing(16)
        options_layout.setVerticalSpacing(8)
        row = 0

        field = PropertyLineEdit()
        button = QtWidgets.QPushButton("Help")
        button.clicked.connect(self.show_help_dialog)
        options_layout.addWidget(field, row, 0)
        options_layout.addWidget(button, row, 1)
        self.controls.options = field
        self.controls.help = button
        row += 1

        options_widget = QtWidgets.QWidget()
        options_widget.setLayout(options_layout)
        options_widget.roll = VerticalRollAnimation(options_widget)
        self.controls.options_widget = options_widget

        self.addLayout(title_layout)
        self.addWidget(options_widget)

    def set_options_visible(self, value: bool):
        self.controls.options_widget.roll.setAnimatedVisible(value)

    def show_help_dialog(self):
        self.help_dialog.show()


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
        self.cards.format_options = FormatOptionsSelector(self)

        self.cards.query.set_placeholder_text("Sequences to match against database contents (FASTA or FASTQ)")
        self.cards.database.set_placeholder_text("Match all query sequences against this database")
        self.cards.output.set_placeholder_text("The output file will be saved here")

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

        self.binder.bind(object.properties.blast_method, self.cards.blast_options.controls.blast_method.setValue)
        self.binder.bind(self.cards.blast_options.controls.blast_method.valueChanged, object.properties.blast_method)

        self.binder.bind(object.properties.blast_outfmt, self.cards.format_options.controls.outfmt.setValue)
        self.binder.bind(self.cards.format_options.controls.outfmt.valueChanged, object.properties.blast_outfmt)
        self.binder.bind(self.cards.format_options.help_dialog.restore_defaults, object.outfmt_restore_defaults)
        self.binder.bind(self.cards.format_options.help_dialog.add_specifier, object.outfmt_add_specifier)
        self.cards.format_options.set_options_visible(object.blast_outfmt_show_more)

        self.binder.bind(self.cards.query.selectedPath, object.properties.output_path, lambda p: p.parent)

        self.binder.bind(object.properties.blast_outfmt_show_more, self.cards.format_options.set_options_visible)

        self.cards.blast_options.controls.blast_num_threads.bind_property(object.properties.blast_num_threads)
        self.cards.blast_options.controls.blast_evalue.bind_property(object.properties.blast_evalue)
        self.cards.format_options.controls.options.bind_property(object.properties.blast_outfmt_options)
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
