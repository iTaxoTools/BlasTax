from PySide6 import QtCore

import multiprocessing
from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.common.utility import override
from itaxotools.taxi_gui.model.tasks import SubtaskModel, TaskModel
from itaxotools.taxi_gui.types import Notification
from itaxotools.taxi_gui.utility import human_readable_seconds

from ..common.types import BlastMethod
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


class Model(TaskModel):
    task_name = title

    batch_mode = Property(bool, False)
    input_query_path = Property(Path, Path())
    input_query_list = Property(PathListModel, Instance)
    input_database_path = Property(Path, Path())
    input_nucleotides_path = Property(Path, Path())
    output_path = Property(Path, Path())

    blast_method = Property(BlastMethod, BlastMethod.blastn)
    blast_evalue = Property(float, 1e-5)
    blast_num_threads = Property(int, 1)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self._update_num_threads_default()

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.properties.batch_mode,
            self.properties.input_query_path,
            self.properties.input_database_path,
            self.properties.input_nucleotides_path,
            self.properties.output_path,
            self.properties.blast_method,
            self.input_query_list.rowsInserted,
            self.input_query_list.rowsRemoved,
            self.input_query_list.modelReset,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if self.batch_mode:
            if not self.input_query_list.paths:
                return False
        if not self.batch_mode:
            if self.input_query_path == Path():
                return False
        if self.input_database_path == Path():
            return False
        if self.output_path == Path():
            return False
        if self.blast_method == BlastMethod.blastx:
            if self.input_nucleotides_path == Path():
                return False
        return True

    def start(self):
        super().start()

        self.exec(
            process.execute,
            batch_mode=self.batch_mode,
            input_query_path=self.input_query_path,
            input_database_path=self.input_database_path,
            input_nucleotides_path=self.input_nucleotides_path,
            input_query_list=self.input_query_list.paths,
            output_path=self.output_path,
            blast_method=self.blast_method.executable,
            blast_evalue=self.blast_evalue or self.properties.blast_evalue.default,
            blast_num_threads=self.blast_num_threads or self.properties.blast_num_threads.default,
        )

    def onDone(self, report):
        time_taken = human_readable_seconds(report.result.seconds_taken)
        self.notification.emit(Notification.Info(f"{self.name} completed successfully!\nTime taken: {time_taken}."))

        self.busy = False

    def _update_num_threads_default(self):
        cpus = multiprocessing.cpu_count()
        property = self.properties.blast_num_threads
        setattr(property._parent, Property.key_default(property._key), cpus)
        property.set(cpus)

    def delete_paths(self, indices: list[int]):
        if not indices:
            return
        self.input_query_list.remove_paths(indices)

    def add_paths(self, paths: list[Path]):
        if not paths:
            return
        self.input_query_list.add_paths(paths)

    def add_folder(self, dir: Path):
        assert dir.is_dir()
        paths = []
        paths += list(dir.glob("*.fa"))
        paths += list(dir.glob("*.fas"))
        paths += list(dir.glob("*.fasta"))
        self.add_paths(paths)

    def open(self, path: Path):
        if path.suffix in [".nin", ".pin"]:
            self.input_database_path = path
        else:
            self.input_query_path = path
            self.output_path = path.parent
