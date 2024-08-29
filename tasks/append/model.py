import multiprocessing
from datetime import datetime
from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BlastTaskModel, PathListModel
from ..common.types import BlastMethod
from ..common.utils import get_database_index_from_path
from . import process, title


class Model(BlastTaskModel):
    task_name = title

    batch_mode = Property(bool, False)
    input_query_path = Property(Path, Path())
    input_query_list = Property(PathListModel, Instance)
    input_query_list_rows = Property(int, 0)
    input_query_list_total = Property(int, 0)
    input_database_path = Property(Path, Path())
    output_path = Property(Path, Path())

    blast_method = Property(BlastMethod, BlastMethod.blastn)
    blast_evalue = Property(float, 1e-5)
    blast_num_threads = Property(int, 1)
    blast_extra_args = Property(str, '-outfmt "6 length pident qseqid sseqid sseq qframe sframe"')

    append_multiple = Property(bool, False)
    append_pident = Property(float, 97.000)
    append_length = Property(int, 0)

    append_timestamp = Property(bool, False)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self._update_num_threads_default()

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.input_query_list.rowsInserted,
            self.input_query_list.rowsRemoved,
            self.input_query_list.modelReset,
        ]:
            self.binder.bind(handle, self._update_input_query_list_rows)
            self.binder.bind(handle, self._update_input_query_list_total)

        for handle in [
            self.properties.batch_mode,
            self.properties.input_query_path,
            self.properties.input_database_path,
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
            if not self.input_query_list.get_all_paths():
                return False
        if not self.batch_mode:
            if self.input_query_path == Path():
                return False
        if self.input_database_path == Path():
            return False
        if self.output_path == Path():
            return False
        return True

    def start(self):
        super().start()
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        self.exec(
            process.execute,
            work_dir=work_dir,
            batch_mode=self.batch_mode,
            input_query_path=self.input_query_path,
            input_database_path=self.input_database_path,
            input_query_list=self.input_query_list.get_all_paths(),
            output_path=self.output_path,
            blast_method=self.blast_method.executable,
            blast_evalue=self.blast_evalue or self.properties.blast_evalue.default,
            blast_num_threads=self.blast_num_threads or self.properties.blast_num_threads.default,
            append_multiple=self.append_multiple,
            append_pident=self.append_pident,
            append_length=self.append_length,
            append_timestamp=self.append_timestamp,
        )

    def _update_num_threads_default(self):
        cpus = multiprocessing.cpu_count()
        property = self.properties.blast_num_threads
        setattr(property._parent, Property.key_default(property._key), cpus)
        property.set(cpus)

    def _update_input_query_list_rows(self):
        self.input_query_list_rows = len(self.input_query_list.paths)

    def _update_input_query_list_total(self):
        self.input_query_list_total = len(self.input_query_list.get_all_paths())

    def delete_paths(self, indices: list[int]):
        if not indices:
            return
        self.input_query_list.remove_paths(indices)

    def clear_paths(self):
        self.input_query_list.clear()

    def add_paths(self, paths: list[Path]):
        if not paths:
            return
        self.input_query_list.add_paths(paths)

    def add_folder(self, dir: Path):
        self.input_query_list.add_paths([dir])

    def open(self, path: Path):
        if db := get_database_index_from_path(path):
            self.input_database_path = db
        else:
            self.input_query_path = path
            self.output_path = path.parent
