from PySide6 import QtCore, QtGui, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.utility import human_readable_seconds
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import GLineEdit, NoWheelComboBox

from ..common.view import (
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OutputDirectorySelector,
)
from . import long_description, pixmap_medium, title
from .types import CODON_TABLES, TrimResults


class FilenameSelector(Card):
    nameChanged = QtCore.Signal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.draw_main(text)

    def draw_main(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        field = GLineEdit()
        field.textEditedSafe.connect(self._handle_name_changed)
        field.setPlaceholderText("---")
        field.setTextMargins(4, 0, 12, 0)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(field, 1)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.label = label
        self.controls.field = field

    def _handle_name_changed(self, name: str):
        self.nameChanged.emit(str(name))

    def set_placeholder_text(self, text: str):
        self.controls.field.setPlaceholderText(text)

    def set_name(self, name: str):
        text = name or ""
        self.controls.field.setText(text)


class OptionSelector(Card):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.draw_title(text)
        self.draw_main()

    def draw_title(self, text):
        title = QtWidgets.QLabel(text + ":")
        title.setStyleSheet("""font-size: 16px;""")
        title.setMinimumWidth(150)
        self.addWidget(title)

    def draw_main(self):
        trim_stop = QtWidgets.QCheckBox("Cut sequences after and including the first encountered stop codon.")
        trim_end = QtWidgets.QCheckBox("Trim sequences to end with a full codon (3rd position).")
        discard_ambiguous = QtWidgets.QCheckBox("Discard sequences with ambiguous reading frames.")
        log = QtWidgets.QCheckBox("Generate a report on ambiguous reading frames.")

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(trim_stop)
        layout.addWidget(trim_end)
        layout.addWidget(discard_ambiguous)
        layout.addWidget(log)

        self.controls.trim_stop = trim_stop
        self.controls.trim_end = trim_end
        self.controls.discard_ambiguous = discard_ambiguous
        self.controls.log = log

        self.addLayout(layout)


class CodonTableSelector(Card):
    code_changed = QtCore.Signal(int)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.draw_main(text)

    def draw_main(self, text):
        title = QtWidgets.QLabel(text + ":")
        title.setStyleSheet("""font-size: 16px;""")
        title.setMinimumWidth(150)

        combo = NoWheelComboBox()
        for id, name in CODON_TABLES.items():
            label = f"{(str(id) + ':').rjust(3)}  {name}"
            combo.addItem(label, id)
        combo.currentIndexChanged.connect(self._handle_index_changed)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(16)
        layout.addWidget(title)
        layout.addWidget(combo, 1)

        self.controls.combo = combo

        self.addLayout(layout)

    def _handle_index_changed(self, index: int):
        code = self.controls.combo.itemData(index)
        self.code_changed.emit(code)

    def set_code(self, code: int):
        index = self.controls.combo.findData(code)
        index = self.controls.combo.setCurrentIndex(index)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.input = BatchQuerySelector("Input sequences", self)
        self.cards.output = OutputDirectorySelector("\u25C0  Output folder", self)
        self.cards.options = OptionSelector("Trimming options", self)
        self.cards.code = CodonTableSelector("Codon table", self)

        self.cards.input.set_batch_only(True)

        self.cards.input.set_placeholder_text("Sequences that will be processed")
        self.cards.output.set_placeholder_text("Folder that will contain all output files")

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

        self.cards.input.bind_batch_model(self.binder, object.input_paths)

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

        self.binder.bind(object.properties.option_trim_stop, self.cards.options.controls.trim_stop.setChecked)
        self.binder.bind(self.cards.options.controls.trim_stop.toggled, object.properties.option_trim_stop)

        self.binder.bind(object.properties.option_trim_end, self.cards.options.controls.trim_end.setChecked)
        self.binder.bind(self.cards.options.controls.trim_end.toggled, object.properties.option_trim_end)

        self.binder.bind(
            object.properties.option_discard_ambiguous, self.cards.options.controls.discard_ambiguous.setChecked
        )
        self.binder.bind(
            self.cards.options.controls.discard_ambiguous.toggled, object.properties.option_discard_ambiguous
        )

        self.binder.bind(object.properties.option_log, self.cards.options.controls.log.setChecked)
        self.binder.bind(self.cards.options.controls.log.toggled, object.properties.option_log)

        self.binder.bind(object.properties.option_code, self.cards.code.set_code)
        self.binder.bind(self.cards.code.code_changed, object.properties.option_code)

        self.binder.bind(object.properties.editable, self.setEditable)

    def report_results(self, task_name: str, results: TrimResults):
        msgBox = QtWidgets.QMessageBox(self.window())
        msgBox.setWindowTitle(app.config.title)
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText(f"{task_name} completed successfully!")
        lc = "\n" if len(results.description) > 20 else " "
        msgBox.setInformativeText(
            f"{results.description}.{lc}Time taken: {human_readable_seconds(results.seconds_taken)}."
        )
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Open)
        button = self.window().msgShow(msgBox)
        if button == QtWidgets.QMessageBox.Open:
            url = QtCore.QUrl.fromLocalFile(str(results.output_path.absolute()))
            QtGui.QDesktopServices.openUrl(url)

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
