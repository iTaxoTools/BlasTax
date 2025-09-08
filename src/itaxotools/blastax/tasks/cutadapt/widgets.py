from PySide6 import QtCore, QtGui, QtWidgets

from itaxotools.taxi_gui.view.widgets import NoWheelComboBox

from .types import CutAdaptAction


class CutAdaptActionComboboxDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        if not index.isValid():
            return

        self.initStyleOption(option, index)
        option.text = index.data(CutAdaptActionCombobox.LabelRole)
        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter)

    def sizeHint(self, option, index):
        height = self.parent().sizeHint().height()
        return QtCore.QSize(0, height)


class CutAdaptActionCombobox(NoWheelComboBox):
    valueChanged = QtCore.Signal(CutAdaptAction)

    DataRole = QtCore.Qt.UserRole
    LabelRole = QtCore.Qt.UserRole + 1

    def __init__(self, actions: list[CutAdaptAction] = list(CutAdaptAction), *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = QtGui.QStandardItemModel()
        for action in actions:
            item = QtGui.QStandardItem()
            item.setData(action.action, QtCore.Qt.DisplayRole)
            item.setData(action.label, self.LabelRole)
            item.setData(action, self.DataRole)
            model.appendRow(item)
        self.setModel(model)

        delegate = CutAdaptActionComboboxDelegate(self)
        self.setItemDelegate(delegate)

        fixed_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        self.setFont(fixed_font)

        metrics = self.fontMetrics()
        length = max([metrics.horizontalAdvance(action.label) for action in CutAdaptAction])
        self.view().setMinimumWidth(length + 16)

        self.currentIndexChanged.connect(self._handle_index_changed)

    def _handle_index_changed(self, index):
        self.valueChanged.emit(self.itemData(index, self.DataRole))

    def setValue(self, value):
        index = self.findData(value, self.DataRole)
        self.setCurrentIndex(index)
