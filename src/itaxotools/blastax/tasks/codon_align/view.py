from PySide6 import QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app

from ..common.view import (
    BatchProgressCard,
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OutputDirectorySelector,
)
from ..mafft.view import AdjustDirectionSelector, StrategySelector
from ..removal.view import CodonTableSelector
from . import long_description, pixmap_medium, title


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = BatchProgressCard(self)
        self.cards.query = BatchQuerySelector("Input sequences", self)
        self.cards.output = OutputDirectorySelector("\u25C0  Output folder", self)
        self.cards.code = CodonTableSelector("Codon table", self)
        self.cards.strategy = StrategySelector(self)
        self.cards.adjust_direction = AdjustDirectionSelector(self)

        self.cards.query.set_placeholder_text("FASTA sequences for alignment")

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

        self.cards.query.bind_batch_model(self.binder, object.input_sequences)

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

        self.binder.bind(object.properties.codon_table, self.cards.code.set_code)
        self.binder.bind(self.cards.code.code_changed, object.properties.codon_table)

        self.binder.bind(object.properties.strategy, self.cards.strategy.set_option)
        self.binder.bind(self.cards.strategy.option_changed, object.properties.strategy)

        self.binder.bind(object.properties.adjust_direction, self.cards.adjust_direction.set_option)
        self.binder.bind(self.cards.adjust_direction.option_changed, object.properties.adjust_direction)

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
