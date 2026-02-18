from PySide6 import QtCore, QtGui, QtWidgets

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import RadioButtonGroup

from ..common.view import (
    BlastTaskView,
    PathDatabaseSelector,
    PathDirectorySelector,
    PathFileOutSelector,
    PathFileSelector,
)
from ..common.widgets import (
    ConsolePropertyLineEdit,
)
from . import long_description, pixmap_medium, title
from .types import OperationMode


class ModeSelectCard(Card):
    modeChanged = QtCore.Signal(OperationMode)

    def __init__(self, title, description, pixmap, parent=None):
        super().__init__(parent)

        label_title = QtWidgets.QLabel(title)
        font = label_title.font()
        font.setPixelSize(18)
        font.setBold(True)
        font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1)
        label_title.setFont(font)

        label_pixmap = QtWidgets.QLabel()
        label_pixmap.setPixmap(pixmap)
        label_pixmap.setFixedSize(pixmap.size())

        mode_layout = QtWidgets.QGridLayout()
        mode_layout.setContentsMargins(0, 6, 0, 4)
        mode_layout.addWidget(label_title, 0, 0, 1, 2)
        mode_layout.setColumnStretch(2, 1)
        mode_layout.setRowMinimumHeight(1, 8)
        mode_layout.setVerticalSpacing(8)
        mode_layout.setHorizontalSpacing(32)

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_value_changed)
        for index, mode in enumerate(OperationMode):
            button = QtWidgets.QRadioButton(mode.label)
            mode_layout.addWidget(button, 2 + index // 2, index % 2)
            group.add(button, mode)

        pixmap_layout = QtWidgets.QVBoxLayout()
        pixmap_layout.setContentsMargins(0, 8, 0, 4)
        pixmap_layout.addWidget(label_pixmap)
        pixmap_layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(16)
        layout.addLayout(pixmap_layout)
        layout.addLayout(mode_layout, 1)
        layout.addSpacing(16)

        self.addLayout(layout)

        self.controls.title = label_title
        self.controls.pixmap = label_pixmap
        self.controls.group = group

    def setTitle(self, text):
        self.controls.title.setText(text)

    def setBusy(self, busy: bool):
        self.setEnabled(not busy)

    def set_mode(self, value: OperationMode):
        self.controls.group.setValue(value)

    def _handle_value_changed(self, value: OperationMode):
        self.modeChanged.emit(value)


class OutfmtSelector(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("Export template:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        field = ConsolePropertyLineEdit()
        self.controls.outfmt = field

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(field, 1)
        layout.setSpacing(16)

        self.addLayout(layout)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = ModeSelectCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.database = PathDatabaseSelector("BLAST database", "in", self)
        self.cards.taxdb = PathDirectorySelector("TaxDB (optional)", "in", self)
        self.cards.fasta_input = PathFileSelector("FASTA input", "in", self)
        self.cards.fasta_output = PathFileOutSelector("FASTA output", "out", self)
        self.cards.output = PathFileOutSelector("Output file", "out", self)
        self.cards.outfmt = OutfmtSelector()

        self.cards.database.set_placeholder_text("Input database for processing")
        self.cards.output.set_placeholder_text("Exported sequence file")
        self.cards.taxdb.set_placeholder_text("Directory containing taxdb.btd and taxdb.bti (leave empty to skip)")
        self.cards.fasta_input.set_placeholder_text(
            "Sequence file with identifiers containing bracket tags in the form of [taxid=...]"
        )
        self.cards.fasta_output.set_placeholder_text(
            "Resulting sequence file with all bracket tags removed from identifiers"
        )

        for card in self.cards:
            card.roll = VerticalRollAnimation(card)

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

        self.binder.bind(object.properties.operation_mode, self.cards.title.set_mode)
        self.binder.bind(self.cards.title.modeChanged, object.properties.operation_mode)

        self.binder.bind(object.properties.show_input_database, self.cards.database.roll.setAnimatedVisible)
        self.binder.bind(object.properties.show_input_taxdb, self.cards.taxdb.roll.setAnimatedVisible)
        self.binder.bind(object.properties.show_output_path, self.cards.output.roll.setAnimatedVisible)
        self.binder.bind(object.properties.show_outfmt, self.cards.outfmt.roll.setAnimatedVisible)
        self.binder.bind(object.properties.show_input_fasta_path, self.cards.fasta_input.roll.setAnimatedVisible)
        self.binder.bind(object.properties.show_output_fasta_path, self.cards.fasta_output.roll.setAnimatedVisible)

        self.binder.bind(object.properties.output_placeholder, self.cards.output.set_placeholder_text)

        self.binder.bind(object.properties.input_database_path, self.cards.database.set_path)
        self.binder.bind(self.cards.database.selectedPath, object.properties.input_database_path)

        self.binder.bind(object.properties.output_path, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_path)

        self.binder.bind(object.properties.blast_taxdb_path, self.cards.taxdb.set_path)
        self.binder.bind(self.cards.taxdb.selectedPath, object.properties.blast_taxdb_path)

        self.binder.bind(object.properties.input_fasta_path, self.cards.fasta_input.set_path)
        self.binder.bind(self.cards.fasta_input.selectedPath, object.properties.input_fasta_path)

        self.binder.bind(object.properties.output_fasta_path, self.cards.fasta_output.set_path)
        self.binder.bind(self.cards.fasta_output.selectedPath, object.properties.output_fasta_path)

        self.cards.outfmt.controls.outfmt.bind_property(object.properties.blast_outfmt, default_placeholder=True)

        self.binder.bind(object.properties.editable, self.setEditable)

    def setEditable(self, editable: bool):
        for card in self.cards:
            card.setEnabled(editable)
        self.cards.progress.setEnabled(True)

    def open(self):
        if self.object.show_input_database:
            self.cards.database._handle_browse()
        else:
            self.cards.fasta_input._handle_browse()
