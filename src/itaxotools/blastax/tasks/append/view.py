from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import GLineEdit, RadioButtonGroup, RichRadioButton

from ..common.types import BlastMethod
from ..common.view import (
    BatchDatabaseSelector,
    BatchProgressCard,
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OptionCard,
    OutputDirectorySelector,
)
from ..common.widgets import (
    BlastMethodCombobox,
    ConsolePropertyLineEdit,
    FloatPropertyLineEdit,
    IntPropertyLineEdit,
    PidentSpinBox,
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
        field = BlastMethodCombobox(
            [
                BlastMethod.blastn,
                BlastMethod.blastp,
                BlastMethod.tblastx,
            ]
        )
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

        name = QtWidgets.QLabel("Locked:")
        field = ConsolePropertyLineEdit()
        field.setReadOnly(True)
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_long_layout.addWidget(name, row, 1)
        options_long_layout.addWidget(field, row, 2)
        self.controls.blast_extra_args = field
        row += 1

        self.addLayout(title_layout)
        self.addLayout(options_layout)
        self.addLayout(options_long_layout)


class MatchOptionSelector(Card):
    mode_changed = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("Sequence selection:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = QtWidgets.QLabel("Determine how matching sequences are retrieved from the database.")

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(label)
        title_layout.addWidget(description, 1)
        title_layout.setSpacing(16)

        mode_layout = QtWidgets.QVBoxLayout()
        mode_layout.setContentsMargins(12, 0, 0, 0)
        mode_layout.setSpacing(8)

        single = RichRadioButton(
            "Single best match,", "matching the longest aligned sequence with the best identity percentage"
        )
        multiple = RichRadioButton("Multiple matches,", "fulfilling certain criteria of length and identity")

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_mode_changed)
        group.add(single, False)
        group.add(multiple, True)
        self.controls.multiple = group

        mode_layout.addWidget(single)
        mode_layout.addWidget(multiple)

        options_layout = QtWidgets.QGridLayout()
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setColumnMinimumWidth(0, 16)
        options_layout.setColumnMinimumWidth(1, 54)
        options_layout.setColumnStretch(3, 1)
        options_layout.setHorizontalSpacing(32)
        options_layout.setVerticalSpacing(8)
        row = 0

        name = QtWidgets.QLabel("Length:")
        field = IntPropertyLineEdit()
        description = QtWidgets.QLabel("Minimum alignment sequence length")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 3)
        self.controls.length = field
        row += 1

        name = QtWidgets.QLabel("Identity:")
        field = PidentSpinBox()
        description = QtWidgets.QLabel("Minimum identity percentage (pident)")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 3)
        self.controls.pident = field
        row += 1

        options_widget = QtWidgets.QWidget()
        options_widget.setLayout(options_layout)
        options_widget.roll = VerticalRollAnimation(options_widget)
        self.controls.options_widget = options_widget

        self.addLayout(title_layout)
        self.addLayout(mode_layout)
        self.addWidget(options_widget)

    def _handle_mode_changed(self, value: bool):
        self.mode_changed.emit(value)
        self.set_options_visible(value)

    def set_mode(self, value: bool):
        self.controls.mode.setValue(value)
        self.set_options_visible(value)

    def set_options_visible(self, value: bool):
        self.controls.options_widget.roll.setAnimatedVisible(value)


class SpecifyIdentifierCard(OptionCard):
    identifierChanged = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.draw_config()

    def draw_config(self):
        label = QtWidgets.QLabel("Identifier: ")
        label.setMinimumWidth(70)

        field = GLineEdit()
        field.textEditedSafe.connect(self._handle_identifier_changed)
        field.setPlaceholderText("---")
        field.setTextMargins(4, 0, 12, 0)

        widget = QtWidgets.QWidget()
        widget.roll = VerticalRollAnimation(widget)

        layout = QtWidgets.QHBoxLayout(widget)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 0, 0, 0)
        layout.addWidget(label)
        layout.addWidget(field)

        self.controls.field = field
        self.controls.options = widget

        self.addWidget(widget)

    def _handle_identifier_changed(self, name: str):
        self.identifierChanged.emit(str(name))

    def set_identifier(self, identifier: str):
        text = identifier or ""
        self.controls.field.setText(text)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = BatchProgressCard(self)
        self.cards.query = BatchQuerySelector("Query sequences", self)
        self.cards.database = BatchDatabaseSelector("BLAST database", self)
        self.cards.output = OutputDirectorySelector("\u25C0  Output folder", self)
        self.cards.blast_options = BlastOptionSelector(self)
        self.cards.match_options = MatchOptionSelector(self)
        self.cards.specify_identifier = SpecifyIdentifierCard(
            "Specify identifier", "Append all hits using the same custom identifier."
        )

        self.cards.query.controls.label.setText("Query mode:")

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

        self.cards.query.bind_batch_model(self.binder, object.input_queries)
        self.cards.database.bind_batch_model(self.binder, object.input_databases)

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

        self.cards.blast_options.controls.blast_num_threads.bind_property(object.properties.blast_num_threads)
        self.cards.blast_options.controls.blast_evalue.bind_property(object.properties.blast_evalue)
        self.cards.blast_options.controls.blast_extra_args.bind_property(object.properties.blast_extra_args)

        self.binder.bind(object.properties.match_multiple, self.cards.match_options.controls.multiple.setValue)
        self.binder.bind(self.cards.match_options.controls.multiple.valueChanged, object.properties.match_multiple)
        self.binder.bind(object.properties.match_pident, self.cards.match_options.controls.pident.setValue)
        self.binder.bind(self.cards.match_options.controls.pident.valueChangedSafe, object.properties.match_pident)
        self.cards.match_options.controls.length.bind_property(object.properties.match_length)
        self.cards.match_options.set_options_visible(object.match_multiple)

        self.binder.bind(
            object.properties.specify_identifier, self.cards.specify_identifier.controls.options.roll.setAnimatedVisible
        )
        self.binder.bind(object.properties.specify_identifier, self.cards.specify_identifier.setChecked)
        self.binder.bind(self.cards.specify_identifier.toggled, object.properties.specify_identifier)
        self.binder.bind(object.properties.specify_identifier_str, self.cards.specify_identifier.set_identifier)
        self.binder.bind(self.cards.specify_identifier.identifierChanged, object.properties.specify_identifier_str)

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
