from PySide6 import QtCore

import os
from pathlib import Path

from itaxotools.common.utility import override
from itaxotools.taxi_gui.loop import ReportDone
from itaxotools.taxi_gui.model.tasks import TaskModel

from ..common.types import Results


class BlastTaskModel(TaskModel):
    reportResults = QtCore.Signal(str, Results)

    def onDone(self, report: ReportDone):
        self.reportResults.emit(self.task_name, report.result)
        self.busy = False


class PathListModel(QtCore.QAbstractListModel):
    def __init__(self, paths=None):
        super().__init__()
        self.paths: list[Path] = paths or []

    @override
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            path = self.paths[index.row()]
            if path.is_dir():
                return str(path.absolute()) + os.path.sep + "*.{fa,fas,fasta}"
            return str(path.absolute())

    @override
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.paths)

    @override
    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def add_paths(self, paths: list[Path]):
        paths = [path for path in paths if path not in self.paths]
        paths.sort()
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount() + len(paths))
        for path in paths:
            self.paths.append(path)
        self.endInsertRows()

    def remove_paths(self, indices: list[int]):
        indices = sorted(indices, reverse=True)
        self.beginRemoveRows(QtCore.QModelIndex(), indices[-1], indices[0])
        for index in indices:
            if 0 <= index < len(self.paths):
                del self.paths[index]
        self.endRemoveRows()

    def clear(self):
        self.beginResetModel()
        self.paths = []
        self.endResetModel()

    def get_all_paths(self):
        all = set()
        for path in self.paths:
            if path.is_file():
                all.add(path)
            elif path.is_dir():
                all.update(path.glob("*.fa"))
                all.update(path.glob("*.fas"))
                all.update(path.glob("*.fasta"))
        return all
