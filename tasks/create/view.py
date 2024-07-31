from PySide6 import QtWidgets

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.tasks import ScrollTaskView

from ..common.view import GraphicTitleCard
from . import long_description, pixmap_medium, title


class View(ScrollTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(
            title, long_description, pixmap_medium.resource, self
        )
        self.cards.progress = ProgressCard(self)

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

        # defined last to override `set_busy` calls
        self.binder.bind(object.properties.editable, self.setEditable)

    def setEditable(self, editable: bool):
        self.cards.title.setEnabled(True)
        self.cards.progress.setEnabled(True)
