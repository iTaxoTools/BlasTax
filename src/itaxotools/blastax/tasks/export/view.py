from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.cards import Card

from ..common.view import (
    BlastTaskView,
    GraphicTitleCard,
    PathDatabaseSelector,
    PathDirectorySelector,
    PathFileOutSelector,
)
from ..common.widgets import (
    ConsolePropertyLineEdit,
)
from . import long_description, pixmap_medium, title


class TaxidInfo(Card):
    check_taxids = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_title()

    def draw_title(self):
        checkbox = QtWidgets.QCheckBox("")
        checkbox.setEnabled(False)
        checkbox.setTristate(True)

        label = QtWidgets.QLabel("Database has TaxID information for each entry?")

        button = QtWidgets.QPushButton("Check")
        button.clicked.connect(self._handle_check)
        button.setFixedWidth(120)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(checkbox)
        layout.addWidget(label, 1)
        layout.addWidget(button)
        layout.setSpacing(12)
        self.addLayout(layout)

        self.controls.checkbox = checkbox
        self.controls.button = button

    def setChecked(self, checked: bool | None):
        if checked is None:
            self.controls.checkbox.setCheckState(QtCore.Qt.PartiallyChecked)
        else:
            self.controls.checkbox.setChecked(checked)

    def _handle_check(self):
        self.check_taxids.emit()


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
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.database = PathDatabaseSelector("\u25B6  BLAST database", self)
        self.cards.taxdb = PathDirectorySelector("\u25B6  TaxDB (optional)", self)
        self.cards.output = PathFileOutSelector("\u25C0  Output file", self)
        self.cards.outfmt = OutfmtSelector()
        self.cards.info = TaxidInfo()

        self.cards.database.set_placeholder_text("Database to be processed")
        self.cards.output.set_placeholder_text("Exported sequence file")
        self.cards.taxdb.set_placeholder_text("Directory containing taxdb.btd and taxdb.bti (leave empty to skip)")

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

        self.binder.bind(object.properties.input_database_path, self.cards.database.set_path)
        self.binder.bind(self.cards.database.selectedPath, object.properties.input_database_path)

        self.binder.bind(object.properties.output_path, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_path)

        self.binder.bind(object.properties.has_taxids, self.cards.info.setChecked)
        self.binder.bind(self.cards.info.check_taxids, object.check_taxids)
        self.binder.bind(
            object.properties.input_database_path, self.cards.info.controls.button.setEnabled, lambda x: x != Path()
        )

        self.binder.bind(object.properties.blast_taxdb_path, self.cards.taxdb.set_path)
        self.binder.bind(self.cards.taxdb.selectedPath, object.properties.blast_taxdb_path)

        self.cards.outfmt.controls.outfmt.bind_property(object.properties.blast_outfmt, default_placeholder=True)

        self.binder.bind(object.properties.editable, self.setEditable)

    def setEditable(self, editable: bool):
        for card in self.cards:
            card.setEnabled(editable)
        self.cards.title.setEnabled(True)
        self.cards.progress.setEnabled(True)

    def open(self):
        self.cards.database._handle_browse()
