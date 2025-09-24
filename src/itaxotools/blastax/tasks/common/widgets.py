from PySide6 import QtCore, QtGui, QtWidgets

from itaxotools.common.bindings import Binder, PropertyRef
from itaxotools.common.utility import Guard, override
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


class ElidedLongLabel(QtWidgets.QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.setWordWrap(True)
        self._full_text = text

        action = QtGui.QAction("&Copy", self)
        action.triggered.connect(self.copy)
        self.addAction(action)

    def setText(self, text):
        self._full_text = text
        self.updateText()

    def resizeEvent(self, event):
        self.updateText()
        super().resizeEvent(event)

    def updateText(self):
        metrics = self.fontMetrics()
        elided_text = metrics.elidedText(self._full_text, QtCore.Qt.ElideRight, self.width())
        super().setText(elided_text)

    def copy(self):
        QtWidgets.QApplication.clipboard().setText(self._full_text)


class FrontEllipsisDelegate(QtWidgets.QStyledItemDelegate):
    rowHeight = 20

    def __init__(self, parent=None):
        super().__init__(parent)

    @override
    def paint(self, painter, option, index):
        painter.save()

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.light().color())
        else:
            painter.fillRect(option.rect, option.palette.base())
            painter.setPen(option.palette.text().color())

        text_rect = option.rect
        text_rect -= QtCore.QMargins(6, 0, 6, 0)

        text = index.data(QtCore.Qt.DisplayRole)
        metrics = QtGui.QFontMetrics(option.font)
        elided_text = metrics.elidedText(text, QtCore.Qt.ElideLeft, text_rect.width())

        painter.drawText(text_rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, elided_text)

        painter.restore()

    @override
    def sizeHint(self, option, index):
        return QtCore.QSize(self.rowHeight, self.rowHeight)


class GrowingListView(QtWidgets.QListView):
    requestDelete = QtCore.Signal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSelectionMode(QtWidgets.QListView.MultiSelection)
        self.setItemDelegate(FrontEllipsisDelegate(self))
        self.height_slack = 12
        self.lines_max = 8
        self.lines_min = 2

    @override
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if any(
            (
                event.key() == QtCore.Qt.Key_Backspace,
                event.key() == QtCore.Qt.Key_Delete,
            )
        ):
            selected = self.selectionModel().selectedIndexes()
            if selected:
                indices = [index.row() for index in selected]
                self.requestDelete.emit(indices)
        super().keyPressEvent(event)

    @override
    def sizeHint(self):
        width = super().sizeHint().width()
        height = self.getHeightHint() + self.height_slack
        return QtCore.QSize(width, height)

    def getHeightHint(self):
        lines = self.model().rowCount() if self.model() else 0
        lines = max(lines, self.lines_min)
        lines = min(lines, self.lines_max)
        height = FrontEllipsisDelegate.rowHeight
        return int(lines * height)


class GTextEdit(QtWidgets.QPlainTextEdit):
    textEditedSafe = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self._handleEdit)
        self._guard = Guard()

    def _handleEdit(self):
        with self._guard:
            self.textEditedSafe.emit(self.toPlainText())

    @override
    def setText(self, text):
        if self._guard:
            return
        super().setPlainText(text)


class GrowingTextEdit(GTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.document().contentsChanged.connect(self.updateGeometry)
        self.height_slack = 20
        self.lines_min = 4
        self.lines_max = 12

    def setPlaceholderText(self, text: str):
        super().setPlaceholderText(text)
        self.lines_min = len(self.placeholderText().splitlines())

    def getHeightHint(self):
        lines = self.document().size().height()
        lines = min(lines, self.lines_max)
        lines = max(lines, self.lines_min)
        height = self.fontMetrics().height()
        return int(lines * height)

    def sizeHint(self):
        width = super().sizeHint().width()
        height = self.getHeightHint() + self.height_slack
        return QtCore.QSize(width, height)


class NoWheelRadioButton(QtWidgets.QRadioButton):
    # Fix scrolling when hovering disabled button
    def event(self, event):
        if isinstance(event, QtGui.QWheelEvent):
            event.ignore()
            return False
        return super().event(event)


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

    def __init__(self, methods: list[BlastMethod] = list(BlastMethod), *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = QtGui.QStandardItemModel()
        for method in methods:
            item = QtGui.QStandardItem()
            item.setData(method.executable, QtCore.Qt.DisplayRole)
            item.setData(method.label, self.LabelRole)
            item.setData(method, self.DataRole)
            model.appendRow(item)
        self.setModel(model)

        delegate = BlastComboboxDelegate(self)
        self.setItemDelegate(delegate)

        fixed_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        self.setFont(fixed_font)

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


class BlastOutfmtFullCombobox(NoWheelComboBox):
    valueChanged = QtCore.Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = QtGui.QStandardItemModel()
        for key, text in BLAST_OUTFMT_OPTIONS.items():
            item = QtGui.QStandardItem()
            prefix = str(key) + ":"
            item.setData(f"{prefix.ljust(3)} {text}", QtCore.Qt.DisplayRole)
            item.setData(key, QtCore.Qt.UserRole)
            model.appendRow(item)
        self.setModel(model)

        self.currentIndexChanged.connect(self._handle_index_changed)

    def _handle_index_changed(self, index):
        self.valueChanged.emit(self.itemData(index, QtCore.Qt.UserRole))

    def setValue(self, value):
        index = self.findData(value, QtCore.Qt.UserRole)
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


class ConsolePropertyLineEdit(BasePropertyLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))
        self.setStyleSheet("GLineEdit { padding: 2px; padding-top: 4px;} ")


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


class GSpinBox(QtWidgets.QSpinBox):
    valueChangedSafe = QtCore.Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("QSpinBox { padding-left: 2px; padding-right: 4px; }")
        self.valueChanged.connect(self._handleEdit)
        self._guard = Guard()

    def _handleEdit(self, value):
        with self._guard:
            self.valueChangedSafe.emit(value)

    @override
    def setValue(self, value):
        if self._guard:
            return
        super().setValue(value)

    @override
    def wheelEvent(self, event):
        event.ignore()


class GDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    valueChangedSafe = QtCore.Signal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("QDoubleSpinBox { padding-left: 2px; padding-right: 4px; }")
        self.valueChanged.connect(self._handleEdit)
        self._guard = Guard()

    def _handleEdit(self, value):
        with self._guard:
            self.valueChangedSafe.emit(value)

    @override
    def setValue(self, value):
        if self._guard:
            return
        super().setValue(value)

    @override
    def wheelEvent(self, event):
        event.ignore()


class BatchQueryHelp(QtWidgets.QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPlaceholderText("Sequences to match against database contents (FASTA or FASTQ)")
        self.setEnabled(False)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
        )

    def sizeHint(self):
        return QtCore.QSize(0, 0)


class PidentSpinBox(GDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedWidth(120)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setSingleStep(1)
        self.setDecimals(3)
        self.setSuffix("%")
        self.setValue(97)
