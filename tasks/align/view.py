from PySide6 import QtCore, QtWidgets

from itaxotools.common.bindings import Binder
from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.tasks import ScrollTaskView
from itaxotools.taxi_gui.view.widgets import RadioButtonGroup

from ..common.view import GraphicTitleCard
from ..common.widgets import ElidedLineEdit, GrowingListView
from . import long_description, pixmap_medium, title


class QuerySelector(Card):
    batchModeChanged = QtCore.Signal(bool)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.binder = Binder()
        self.draw_main(text)
        self.draw_single("Query FASTA file")
        self.draw_batch("Query FASTA files")

    def draw_main(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(140)

        single = QtWidgets.QRadioButton("Single file")
        batch = QtWidgets.QRadioButton("Batch mode")

        group = RadioButtonGroup()
        group.valueChanged.connect(self._handle_batch_mode_changed)
        group.add(single, False)
        group.add(batch, True)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(single)
        layout.addWidget(batch, 1)
        layout.addSpacing(136)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.label = label
        self.controls.single = single
        self.controls.batch = batch
        self.controls.batch_mode = group

    def draw_single(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setMinimumWidth(140)

        field = ElidedLineEdit()
        # field.textEditedSafe.connect(self._handle_text_changed)
        field.setReadOnly(True)

        browse = QtWidgets.QPushButton("Browse")
        # browse.clicked.connect(self._handle_browse)
        browse.setFixedWidth(120)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label)
        layout.addWidget(field, 1)
        layout.addWidget(browse)
        layout.setSpacing(16)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.addWidget(widget)
        widget.roll = VerticalRollAnimation(widget)

        self.controls.single_query = widget

    def draw_batch(self, text):
        label = QtWidgets.QLabel(text + ":")
        label.setMinimumWidth(140)

        view = GrowingListView()

        add_file = QtWidgets.QPushButton("Add file")
        add_folder = QtWidgets.QPushButton("Add folder")
        remove = QtWidgets.QPushButton("Remove")
        remove.setFixedWidth(120)

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label, 0, 0)
        layout.addWidget(view, 0, 1, 4, 1)
        layout.addWidget(add_file, 0, 2)
        layout.addWidget(add_folder, 1, 2)
        layout.addWidget(remove, 2, 2)
        layout.setHorizontalSpacing(16)
        layout.setVerticalSpacing(8)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.addWidget(widget)
        widget.roll = VerticalRollAnimation(widget)

        self.controls.batch_query = widget

    def _handle_batch_mode_changed(self, value):
        self.batchModeChanged.emit(value)

    def set_batch_mode(self, value: bool):
        self.controls.batch_mode.setValue(value)
        self.controls.batch_query.roll.setAnimatedVisible(value)
        self.controls.single_query.roll.setAnimatedVisible(not value)


class View(ScrollTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = ProgressCard(self)
        self.cards.query = QuerySelector("Input mode", self)

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

        self.binder.bind(object.properties.batch_mode, self.cards.query.set_batch_mode)
        self.binder.bind(self.cards.query.batchModeChanged, object.properties.batch_mode)

        # defined last to override `set_busy` calls
        self.binder.bind(object.properties.editable, self.setEditable)

    def setEditable(self, editable: bool):
        self.cards.title.setEnabled(True)
        self.cards.progress.setEnabled(True)
