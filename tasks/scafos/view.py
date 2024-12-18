from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import RadioButtonGroup, RichRadioButton

from ..common.view import (
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OptionCard,
    OutputDirectorySelector,
)
from . import long_description, pixmap_medium, title
from .types import AmalgamationMethodTexts, TagMethodTexts


class TagMethodSelector(Card):
    method_changed = QtCore.Signal(TagMethodTexts)

    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("Species detection:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = QtWidgets.QLabel("Determine how species are inferred from sequence identifiers.")

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(label)
        title_layout.addWidget(description, 1)
        title_layout.setSpacing(16)

        mode_layout = QtWidgets.QVBoxLayout()
        mode_layout.setContentsMargins(12, 0, 0, 0)
        mode_layout.setSpacing(8)

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_method_changed)
        self.controls.method = group

        for method in TagMethodTexts:
            button = RichRadioButton(f"{method.title}:", f"{method.description}.")
            group.add(button, method)
            mode_layout.addWidget(button)

        self.addLayout(title_layout)
        self.addLayout(mode_layout)

    def _handle_method_changed(self, value: TagMethodTexts):
        self.method_changed.emit(value)

    def set_method(self, value: bool):
        self.controls.method.setValue(value)


class AmalgamationMethodSelector(Card):
    method_changed = QtCore.Signal(AmalgamationMethodTexts)

    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("Amalgamation:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = QtWidgets.QLabel("Determine how sequence chimeras are created for each species.")

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(label)
        title_layout.addWidget(description, 1)
        title_layout.setSpacing(16)

        mode_layout = QtWidgets.QVBoxLayout()
        mode_layout.setContentsMargins(12, 0, 0, 0)
        mode_layout.setSpacing(8)

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_method_changed)
        self.controls.method = group

        for method in AmalgamationMethodTexts:
            button = RichRadioButton(f"{method.title}:", f"{method.description}.")
            group.add(button, method)
            mode_layout.addWidget(button)

        self.addLayout(title_layout)
        self.addLayout(mode_layout)

    def _handle_method_changed(self, value: AmalgamationMethodTexts):
        self.method_changed.emit(value)

    def set_method(self, value: bool):
        self.controls.method.setValue(value)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.query = BatchQuerySelector("Input sequences", self)
        self.cards.output = OutputDirectorySelector("\u25C0  Output folder", self)
        self.cards.tag_method = TagMethodSelector(self)
        self.cards.amalgamation_method = AmalgamationMethodSelector(self)
        self.cards.report = OptionCard(
            "Save reports:", "Report p-distance pairs and mean species distance for each input file.", self
        )

        self.cards.query.set_placeholder_text("Input sequences for amalgamation (FASTA, FASTQ or ALI)")
        self.cards.report.roll = VerticalRollAnimation(self.cards.report)

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

        self.binder.bind(object.properties.tag_method, self.cards.tag_method.set_method)
        self.binder.bind(self.cards.tag_method.method_changed, object.properties.tag_method)

        self.binder.bind(object.properties.amalgamation_method, self.cards.amalgamation_method.set_method)
        self.binder.bind(self.cards.amalgamation_method.method_changed, object.properties.amalgamation_method)

        self.binder.bind(
            object.properties.amalgamation_method,
            self.cards.report.roll.setAnimatedVisible,
            proxy=lambda x: x == AmalgamationMethodTexts.ByMinimumDistance,
        )

        self.binder.bind(object.properties.save_reports, self.cards.report.setChecked)
        self.binder.bind(self.cards.report.toggled, object.properties.save_reports)

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
