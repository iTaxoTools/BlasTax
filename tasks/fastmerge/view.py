from PySide6 import QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard

from ..common.view import (
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    PathDirectorySelector,
)
from . import long_description, pixmap_medium, title


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.input = BatchQuerySelector("Input sequences", self)
        self.cards.output = PathDirectorySelector("\u25C0  Output folder", self)

        self.cards.input.controls.header.setVisible(False)
        self.cards.input.controls.single_query.roll._visible_target = False
        self.cards.input.controls.batch_query.roll._visible_target = True
        self.cards.input.set_placeholder_text("Folder that contains the FASTA files to be merged")
        self.cards.output.set_placeholder_text("All merged FASTA files will be saved here")

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

        self.cards.input.bind_batch_model(self.binder, object.input_sequences)

        self.binder.bind(object.properties.editable, self.setEditable)

    def setEditable(self, editable: bool):
        for card in self.cards:
            card.setEnabled(editable)
        self.cards.title.setEnabled(True)
        self.cards.progress.setEnabled(True)

    def open(self):
        filename = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self.window(),
            caption=f"{app.config.title} - Open folder",
        )
        if not filename:
            return
        self.object.open(Path(filename))
