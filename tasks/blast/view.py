from PySide6 import QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card

from ..common.view import BlastTaskView, GraphicTitleCard, PathDatabaseSelector, PathDirectorySelector, PathFileSelector
from ..common.widgets import (
    BasePropertyLineEdit,
    BlastMethodCombobox,
    BlastOutfmtCombobox,
    FloatPropertyLineEdit,
    IntPropertyLineEdit,
    PropertyLineEdit,
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
        field = BasePropertyLineEdit()
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


class FormatOptionsSelector(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("BLAST output format:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = QtWidgets.QLabel("Alignment view options for output file format (outfmt)")
        description.setStyleSheet("QLabel {padding-top: 3px;}")

        outfmt = BlastOutfmtCombobox()
        outfmt.setFixedWidth(120)
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
        options_layout.addWidget(field, row, 0)
        options_layout.addWidget(button, row, 1)
        self.controls.options = field
        self.controls.help = button
        row += 1

        options_widget = QtWidgets.QWidget()
        options_widget.setLayout(options_layout)
        options_widget.roll = VerticalRollAnimation(options_widget)
        options_widget.roll._visible_target = True
        self.controls.options_widget = options_widget

        self.addLayout(title_layout)
        self.addWidget(options_widget)

    def set_options_visible(self, value: bool):
        self.controls.options_widget.roll.setAnimatedVisible(value)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.query = PathFileSelector("\u25C0  Query FASTA file", self)
        self.cards.database = PathDatabaseSelector("\u25C0  BLAST database", self)
        self.cards.blast_options = BlastOptionsSelector(self)
        self.cards.format_options = FormatOptionsSelector(self)
        self.cards.output = PathDirectorySelector("\u25B6  Output folder", self)

        self.cards.query.set_placeholder_text("Sequences to match against database contents")
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
        self.binder.bind(object.reportResults, self.report_results)
        self.binder.bind(object.progression, self.cards.progress.showProgress)

        self.binder.bind(object.properties.name, self.cards.title.setTitle)
        self.binder.bind(object.properties.busy, self.cards.progress.setVisible)

        self.binder.bind(object.properties.input_query_path, self.cards.query.set_path)
        self.binder.bind(self.cards.query.selectedPath, object.properties.input_query_path)

        self.binder.bind(object.properties.input_database_path, self.cards.database.set_path)
        self.binder.bind(self.cards.database.selectedPath, object.properties.input_database_path)

        self.binder.bind(object.properties.output_path, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_path)

        self.binder.bind(object.properties.blast_method, self.cards.blast_options.controls.blast_method.setValue)
        self.binder.bind(self.cards.blast_options.controls.blast_method.valueChanged, object.properties.blast_method)

        self.binder.bind(object.properties.blast_outfmt, self.cards.format_options.controls.outfmt.setValue)
        self.binder.bind(self.cards.format_options.controls.outfmt.valueChanged, object.properties.blast_outfmt)

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
