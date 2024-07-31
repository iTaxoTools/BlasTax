from PySide6 import QtCore, QtGui, QtWidgets

from itaxotools.common.utility import override
from itaxotools.taxi_gui.view.widgets import GLineEdit


class ElidedLineEdit(GLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextMargins(4, 0, 12, 0)
        self.full_text = ""

    @override
    def setText(self, text):
        if self._guard:
            return
        self.full_text = text
        self.updateElidedText()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateElidedText()

    def updateElidedText(self):
        metrics = QtGui.QFontMetrics(self.font())
        length = self.width() - self.textMargins().left() - self.textMargins().right()
        elided_text = metrics.elidedText(self.full_text, QtCore.Qt.ElideLeft, length)
        QtWidgets.QLineEdit.setText(self, elided_text)

    def text(self):
        return self.full_text
