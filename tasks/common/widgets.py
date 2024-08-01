from PySide6 import QtCore, QtGui, QtWidgets

from itaxotools.common.utility import override
from itaxotools.taxi_gui.view.widgets import GLineEdit, NoWheelComboBox

from .types import BlastMethod


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


class GrowingListView(QtWidgets.QListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.height_slack = 16
        self.lines_max = 16
        self.lines_min = 8

    def getHeightHint(self):
        lines = self.model().rowCount() if self.model() else 0
        lines = max(lines, self.lines_min)
        lines = min(lines, self.lines_max)
        height = self.fontMetrics().height()
        return int(lines * height)

    def sizeHint(self):
        width = super().sizeHint().width()
        height = self.getHeightHint() + 16
        return QtCore.QSize(width, height)


class BlastMethodDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        if not index.isValid():
            return

        self.initStyleOption(option, index)
        option.text = index.data(BlastMethodCombobox.LabelRole)
        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter)

    def sizeHint(self, option, index):
        height = self.parent().sizeHint().height()
        return QtCore.QSize(0, height)


class BlastMethodCombobox(NoWheelComboBox):
    valueChanged = QtCore.Signal(BlastMethod)

    DataRole = QtCore.Qt.UserRole
    LabelRole = QtCore.Qt.UserRole + 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = QtGui.QStandardItemModel()
        for method in BlastMethod:
            item = QtGui.QStandardItem()
            item.setData(method.executable, QtCore.Qt.DisplayRole)
            item.setData(method.label, self.LabelRole)
            item.setData(method, self.DataRole)
            model.appendRow(item)
        self.setModel(model)

        delegate = BlastMethodDelegate(self)
        self.setItemDelegate(delegate)

        metrics = self.fontMetrics()
        length = max([metrics.horizontalAdvance(method.label) for method in BlastMethod])
        self.view().setMinimumWidth(length + 16)

        self.currentIndexChanged.connect(self._handle_index_changed)

    def _handle_index_changed(self, index):
        self.valueChanged.emit(self.itemData(index, self.DataRole))

    def setValue(self, value):
        index = self.findData(value, self.DataRole)
        self.setCurrentIndex(index)
