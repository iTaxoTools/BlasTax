from PySide6 import QtWidgets

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.tasks import ScrollTaskView

from ..common.view import GraphicTitleCard, PathDatabaseSelector, PathDirectorySelector, PathFileSelector
from ..common.widgets import (
    BasePropertyLineEdit,
    BlastMethodCombobox,
    BlastOutfmtCombobox,
    FloatPropertyLineEdit,
    IntPropertyLineEdit,
)
from . import long_description, pixmap_medium, title


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
        field = BlastMethodCombobox()
        description = QtWidgets.QLabel("Sequence comparison type between query and database")
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

        name = QtWidgets.QLabel("Outfmt:")
        field = BlastOutfmtCombobox()
        description = QtWidgets.QLabel("Alignment view options for output file")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 3)
        self.controls.blast_outfmt = field
        row += 1

        options_long_layout = QtWidgets.QGridLayout()
        options_long_layout.setColumnMinimumWidth(0, 16)
        options_long_layout.setColumnMinimumWidth(1, 54)
        options_long_layout.setColumnStretch(2, 1)
        options_long_layout.setHorizontalSpacing(32)
        options_long_layout.setVerticalSpacing(8)
        row = 0

        name = QtWidgets.QLabel("Format:")
        field = BasePropertyLineEdit()
        field.setPlaceholderText("Set output columns using space delimited specifiers (when outfmt is 6, 7 or 10)")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_long_layout.addWidget(name, row, 1)
        options_long_layout.addWidget(field, row, 2)
        self.controls.blast_outfmt_options = field
        row += 1

        name = QtWidgets.QLabel("Extras:")
        field = BasePropertyLineEdit()
        field.setPlaceholderText("Extra arguments to pass to the BLAST+ executable")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_long_layout.addWidget(name, row, 1)
        options_long_layout.addWidget(field, row, 2)
        self.controls.blast_extra_args = field
        row += 1

        self.addLayout(title_layout)
        self.addLayout(options_layout)
        self.addLayout(options_long_layout)


class View(ScrollTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.query = PathFileSelector("\u25C0  Input FASTA file", self)
        self.cards.database = PathDatabaseSelector("\u25C0  BLAST database", self)
        self.cards.options = OptionsSelector(self)
        self.cards.output = PathDirectorySelector("\u25B6  Output folder", self)

        self.cards.query.set_placeholder_text("Sequences to match against database contents")
        self.cards.database.set_placeholder_text("Match all queries against this database")
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
        self.binder.bind(object.progression, self.cards.progress.showProgress)

        self.binder.bind(object.properties.name, self.cards.title.setTitle)
        self.binder.bind(object.properties.busy, self.cards.progress.setVisible)

        self.binder.bind(object.properties.input_query_path, self.cards.query.set_path)
        self.binder.bind(self.cards.query.selectedPath, object.properties.input_query_path)

        self.binder.bind(object.properties.input_database_path, self.cards.database.set_path)
        self.binder.bind(self.cards.database.selectedPath, object.properties.input_database_path)

        self.binder.bind(object.properties.output_path, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_path)

        self.binder.bind(object.properties.blast_method, self.cards.options.controls.blast_method.setValue)
        self.binder.bind(self.cards.options.controls.blast_method.valueChanged, object.properties.blast_method)

        self.binder.bind(object.properties.blast_outfmt, self.cards.options.controls.blast_outfmt.setValue)
        self.binder.bind(self.cards.options.controls.blast_outfmt.valueChanged, object.properties.blast_outfmt)

        self.binder.bind(self.cards.query.selectedPath, object.properties.output_path, lambda p: p.parent)

        self.binder.bind(
            object.properties.blast_outfmt_show_more, self.cards.options.controls.blast_outfmt_options.setEnabled
        )

        self.cards.options.controls.blast_num_threads.bind_property(object.properties.blast_num_threads)
        self.cards.options.controls.blast_evalue.bind_property(object.properties.blast_evalue)
        self.cards.options.controls.blast_outfmt_options.bind_property(object.properties.blast_outfmt_options)
        self.cards.options.controls.blast_extra_args.bind_property(object.properties.blast_extra_args)

        self.binder.bind(object.properties.editable, self.setEditable)

    def setEditable(self, editable: bool):
        self.cards.query.setEnabled(editable)
        self.cards.database.setEnabled(editable)
        self.cards.options.setEnabled(editable)
        self.cards.output.setEnabled(editable)
