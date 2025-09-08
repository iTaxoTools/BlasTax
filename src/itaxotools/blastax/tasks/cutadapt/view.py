from PySide6 import QtGui, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.widgets import LongLabel

from ..common.view import (
    BatchProgressCard,
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OptionCard,
    OutputDirectorySelector,
)
from ..common.widgets import (
    GrowingTextEdit,
)
from . import long_description, pixmap_medium, title


class AdapterSelector(OptionCard):
    title_text = "Title text"
    list_text = "List text."
    list_placeholder = "List placeholder..."

    def __init__(self, parent=None):
        super().__init__(self.title_text, "", parent)
        self.controls.title.setFixedWidth(250)
        self.draw_list()

    def draw_list(self):
        label = LongLabel(self.list_text)

        list = GrowingTextEdit()
        list.document().setDocumentMargin(8)
        list.setPlaceholderText(self.list_placeholder)
        fixed_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        list.setFont(fixed_font)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(label)
        layout.addWidget(list, 1)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.roll = VerticalRollAnimation(widget)
        self.controls.options_widget = widget
        self.controls.list = list

        self.toggled.connect(self.set_options_visible)

        self.addWidget(widget)

    def set_options_visible(self, value: bool):
        self.controls.options_widget.roll.setAnimatedVisible(value)


class AdapterASelector(AdapterSelector):
    title_text = "Cut 3’ adapters (trim after)"
    list_text = (
        "Enter a list of 3’ adapters separated by new lines. "
        "A 3’ adapter is assumed to be ligated to the 3’ end of your sequences of interest. "
        "When such an adapter is found, the adapter sequence itself and the sequence following it (if there is any) are trimmed. "
        "You may use Cutadapt's syntax to define anchored, non-internal, linked adapters or adapter-specific parameters. "
        "In the examples below, replace 'ADAPTER' with the actual nucleotide sequence of your adapter. "
    )
    list_placeholder = (
        "ADAPTER  -> regular 3’ adapter, full or partial"
        "\n"
        "ADAPTER$ -> anchored 3’, must be at sequence end, full matches only"
        "\n"
        "ADAPTERX -> non-internal 3’, like anchored but can be partial"
        "\n"
        "ADAPTER1...ADAPTER2 -> linked adapters, ^ADAPTER1 and ADAPTER2$ make adapters mandatory"
        "\n"
        "ADAPTER;e=0.2;o=5 -> adapter with maximum error rate = 0.2 and minimum overlap = 5"
    )


class AdapterGSelector(AdapterSelector):
    title_text = "Cut 5’ adapters (trim before)"
    list_text = (
        "Enter a list of 5’ adapters separated by new lines. "
        "A 5’ adapter is assumed to be ligated to the 5’ end of your sequences of interest. "
        "When such an adapter is found, the adapter sequence itself and the sequence preceding it (if there is any) are trimmed. "
        "You may use Cutadapt's syntax to define anchored, non-internal adapters or adapter-specific parameters (see examples below). "
        "In the examples below, replace 'ADAPTER' with the actual nucleotide sequence of your adapter. "
    )
    list_placeholder = (
        " ADAPTER -> regular 5’ adapter, full or partial"
        "\n"
        "^ADAPTER -> anchored 5’, must be at sequence start, full matches only"
        "\n"
        "XADAPTER -> non-internal 5’, like anchored but can be partial"
        "\n"
        " ADAPTER;e=0.2;o=5 -> adapter with maximum error rate = 0.2 and minimum overlap = 5"
    )


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = BatchProgressCard(self)
        self.cards.input = BatchQuerySelector("Input sequences", self)
        self.cards.output = OutputDirectorySelector("\u25C0  Output folder", self)
        self.cards.adapters_a = AdapterASelector(self)
        self.cards.adapters_g = AdapterGSelector(self)
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

        self.binder.bind(object.properties.output_dir, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_dir)

        self.binder.bind(
            object.properties.append_configuration, self.cards.output.controls.append_configuration.setChecked
        )
        self.binder.bind(
            self.cards.output.controls.append_configuration.toggled, object.properties.append_configuration
        )

        self.binder.bind(object.properties.adapters_a_enabled, self.cards.adapters_a.setChecked)
        self.binder.bind(self.cards.adapters_a.toggled, object.properties.adapters_a_enabled)
        self.cards.adapters_a.set_options_visible(object.adapters_a_enabled)

        self.binder.bind(object.properties.adapters_g_enabled, self.cards.adapters_g.setChecked)
        self.binder.bind(self.cards.adapters_g.toggled, object.properties.adapters_g_enabled)
        self.cards.adapters_g.set_options_visible(object.adapters_g_enabled)

        self.binder.bind(object.properties.adapters_a_list, self.cards.adapters_a.controls.list.setText)
        self.binder.bind(self.cards.adapters_a.controls.list.textEditedSafe, object.properties.adapters_a_list)

        self.binder.bind(object.properties.adapters_g_list, self.cards.adapters_g.controls.list.setText)
        self.binder.bind(self.cards.adapters_g.controls.list.textEditedSafe, object.properties.adapters_g_list)

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
