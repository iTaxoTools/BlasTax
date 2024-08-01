from PySide6 import QtCore, QtGui, QtWidgets

from itaxotools.common.bindings import Binder, PropertyRef
from itaxotools.common.utility import override
from itaxotools.taxi_gui.utility import type_convert
from itaxotools.taxi_gui.view.widgets import GLineEdit, NoWheelComboBox

from .types import BLAST_OUTFMT_OPTIONS, BlastMethod


class ElidedLineEdit(GLineEdit):
    textDeleted = QtCore.Signal()

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

    @override
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateElidedText()

    @override
    def focusInEvent(self, event):
        QtCore.QTimer.singleShot(0, self.selectAll)
        return super().focusInEvent(event)

    @override
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if any(
            (
                event.key() == QtCore.Qt.Key_Backspace,
                event.key() == QtCore.Qt.Key_Delete,
            )
        ):
            self.textDeleted.emit()
        super().keyPressEvent(event)

    @override
    def text(self):
        return self.full_text

    def updateElidedText(self):
        metrics = QtGui.QFontMetrics(self.font())
        length = self.width() - self.textMargins().left() - self.textMargins().right() - 8
        elided_text = metrics.elidedText(self.full_text, QtCore.Qt.ElideLeft, length)
        QtWidgets.QLineEdit.setText(self, elided_text)


class GrowingListView(QtWidgets.QListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSelectionMode(QtWidgets.QListView.MultiSelection)
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


class BlastComboboxDelegate(QtWidgets.QStyledItemDelegate):
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

        delegate = BlastComboboxDelegate(self)
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


class BlastOutfmtCombobox(NoWheelComboBox):
    valueChanged = QtCore.Signal(int)

    DataRole = QtCore.Qt.UserRole
    LabelRole = QtCore.Qt.UserRole + 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = QtGui.QStandardItemModel()
        for key, text in BLAST_OUTFMT_OPTIONS.items():
            item = QtGui.QStandardItem()
            item.setData(str(key), QtCore.Qt.DisplayRole)
            item.setData(f"{str(key).rjust(2)}: {text}", self.LabelRole)
            item.setData(key, self.DataRole)
            model.appendRow(item)
        self.setModel(model)

        delegate = BlastComboboxDelegate(self)
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


class BasePropertyLineEdit(GLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTextMargins(2, 0, 12, 0)
        self.binder = Binder()
        self.proxy_in = lambda x: x
        self.proxy_out = lambda x: x

    def bind_property(self, property: PropertyRef):
        self.binder.unbind_all()
        self.binder.bind(property, self.setText, proxy=self.proxy_in)
        self.binder.bind(self.textEditedSafe, property, proxy=self.proxy_out)


class PropertyLineEdit(BasePropertyLineEdit):
    def bind_property(self, property: PropertyRef):
        super().bind_property(property)
        self.setPlaceholderText(self.proxy_in(property.default))


class IntPropertyLineEdit(PropertyLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy_in = lambda x: type_convert(x, str, "")
        self.proxy_out = lambda x: type_convert(x, int, 0)
        validator = QtGui.QIntValidator()
        self.setValidator(validator)


class FloatPropertyLineEdit(PropertyLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy_in = lambda x: type_convert(x, str, "")
        self.proxy_out = lambda x: type_convert(x, float, 0)
        validator = QtGui.QDoubleValidator()
        self.setValidator(validator)
