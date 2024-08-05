from PySide6 import QtCore

import multiprocessing
from pathlib import Path

from itaxotools.common.bindings import Property
from itaxotools.common.utility import override
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BlastTaskModel
from ..common.types import BLAST_OUTFMT_SPECIFIERS_TABLE, BlastMethod
from ..common.utils import get_database_index_from_path
from . import process, title


class PathListModel(QtCore.QAbstractListModel):
    def __init__(self, paths=None):
        super().__init__()
        self.paths = paths or []

    @override
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            path = self.paths[index.row()]
            return str(path.absolute())

    @override
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.paths)

    @override
    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def add_paths(self, paths: list[Path]):
        paths = [path for path in paths if path not in self.paths]
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


class Model(BlastTaskModel):
    task_name = title

    input_query_path = Property(Path, Path())
    input_database_path = Property(Path, Path())
    output_path = Property(Path, Path())

    blast_method = Property(BlastMethod, BlastMethod.blastn)
    blast_evalue = Property(float, 1e-5)
    blast_num_threads = Property(int, 1)
    blast_outfmt = Property(int, 0)
    blast_outfmt_show_more = Property(bool, False)
    blast_outfmt_options = Property(str, "")
    blast_extra_args = Property(str, "")

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self._update_num_threads_default()
        self.binder.bind(
            self.properties.blast_outfmt,
            self.properties.blast_outfmt_show_more,
            proxy=lambda x: x in BLAST_OUTFMT_SPECIFIERS_TABLE.keys(),
        )

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.properties.input_query_path,
            self.properties.input_database_path,
            self.properties.output_path,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if self.input_query_path == Path():
            return False
        if self.input_database_path == Path():
            return False
        if self.output_path == Path():
            return False
        return True

    def start(self):
        super().start()

        self.exec(
            process.execute,
            input_query_path=self.input_query_path,
            input_database_path=self.input_database_path,
            output_path=self.output_path,
            blast_method=self.blast_method.executable,
            blast_evalue=self.blast_evalue or self.properties.blast_evalue.default,
            blast_num_threads=self.blast_num_threads or self.properties.blast_num_threads.default,
            blast_outfmt=self.blast_outfmt or self.properties.blast_outfmt.default,
            blast_outfmt_options=self.blast_outfmt_options,
            blast_extra_args=self.blast_extra_args,
        )

    def _update_num_threads_default(self):
        cpus = multiprocessing.cpu_count()
        property = self.properties.blast_num_threads
        setattr(property._parent, Property.key_default(property._key), cpus)
        property.set(cpus)

    def open(self, path: Path):
        if db := get_database_index_from_path(path):
            self.input_database_path = db
        else:
            self.input_query_path = path
            self.output_path = path.parent
