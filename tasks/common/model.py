from PySide6 import QtCore

import os
from pathlib import Path

from itaxotools.common.bindings import Binder, Instance, Property, PropertyObject
from itaxotools.common.utility import override
from itaxotools.taxi_gui.loop import DataQuery
from itaxotools.taxi_gui.model.tasks import TaskModel
from itaxotools.taxi_gui.threading import ReportDone, ReportStop

from ..common.types import Results


class BlastTaskModel(TaskModel):
    report_results = QtCore.Signal(str, Results)
    request_confirmation = QtCore.Signal(object, object, object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.binder.bind(self.query, self.onQuery)

    def onDone(self, report: ReportDone):
        self.report_results.emit(self.task_name, report.result)
        self.busy = False

    def onQuery(self, query: DataQuery):
        self.request_confirmation.emit(
            query.data,
            lambda: self.answer(True),
            lambda: self.answer(False),
        )

    def onStop(self, report: ReportStop):
        self.busy = False


class PathListModel(QtCore.QAbstractListModel):
    def __init__(self, paths=None):
        super().__init__()
        self.paths: list[Path] = paths or []
        self.globs = ["fa", "fas", "fasta", "fq", "fastq"]

    @override
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            path = self.paths[index.row()]
            if path.is_dir():
                if self.globs:
                    globs = ",".join(self.globs)
                    return str(path.absolute()) + os.path.sep + f"*.{{{globs}}}"
                else:
                    return str(path.absolute()) + os.path.sep + "*"
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
                if self.globs:
                    for glob in self.globs:
                        all.update(path.glob(f"*.{glob}"))
                else:
                    all.update(x for x in path.iterdir() if x.is_file())
        return all


class BatchQueryModel(PropertyObject):
    batch_mode = Property(bool, False)
    query_path = Property(Path, Path())
    query_list = Property(PathListModel, Instance)
    query_list_rows = Property(int, 0)
    query_list_total = Property(int, 0)
    parent_path = Property(Path, Path())

    ready = Property(bool, False)

    def __init__(self):
        super().__init__()
        self.binder = Binder()

        for handle in [
            self.query_list.rowsInserted,
            self.query_list.rowsRemoved,
            self.query_list.modelReset,
        ]:
            self.binder.bind(handle, self._update_query_list_rows)
            self.binder.bind(handle, self._update_query_list_total)

        for handle in [
            self.properties.batch_mode,
            self.properties.query_path,
            self.query_list.rowsInserted,
            self.query_list.rowsRemoved,
            self.query_list.modelReset,
        ]:
            self.binder.bind(handle, self.check_ready)

        self.binder.bind(self.properties.batch_mode, self.update_parent_path)

        self.check_ready()

    def check_ready(self):
        self.ready = self.is_ready()

    def is_ready(self):
        if self.batch_mode:
            if not self.query_list.get_all_paths():
                return False
        if not self.batch_mode:
            if self.query_path == Path():
                return False
        return True

    def get_all_paths(self):
        if self.batch_mode:
            return self.query_list.get_all_paths()
        return [self.query_path]

    def _update_query_list_rows(self):
        self.query_list_rows = len(self.query_list.paths)

    def _update_query_list_total(self):
        self.query_list_total = len(self.query_list.get_all_paths())

    def set_globs(self, globs: list[str]):
        self.query_list.globs = globs

    def delete_paths(self, indices: list[int]):
        if not indices:
            return
        self.query_list.remove_paths(indices)
        self.update_parent_path()

    def clear_paths(self):
        self.query_list.clear()
        self.update_parent_path()

    def add_paths(self, paths: list[Path]):
        if not paths:
            return
        self.query_list.add_paths(paths)
        self.update_parent_path()

    def add_folder(self, dir: Path):
        self.query_list.add_paths([dir])
        self.update_parent_path()

    def set_path(self, path: Path):
        self.query_path = path
        self.update_parent_path()

    def update_parent_path(self):
        if self.batch_mode:
            paths = self.query_list.paths
            if not paths:
                self.parent_path = Path()
            else:
                first: Path = paths[0]
                if first.is_dir():
                    self.parent_path = first
                else:
                    self.parent_path = first.parent
        else:
            self.parent_path = self.query_path.parent

    def open(self, path: Path):
        if self.batch_mode:
            self.add_paths([path])
        else:
            self.set_path(path)
