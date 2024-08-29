import multiprocessing
from datetime import datetime
from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BatchQueryModel, BlastTaskModel
from ..common.types import BlastMethod
from ..common.utils import get_database_index_from_path
from . import process, title


class Model(BlastTaskModel):
    task_name = title

    input_queries = Property(BatchQueryModel, Instance)
    input_database_path = Property(Path, Path())
    input_nucleotides_path = Property(Path, Path())
    output_path = Property(Path, Path())

    blast_method = Property(BlastMethod, BlastMethod.blastx)
    blast_evalue = Property(float, 1e-5)
    blast_num_threads = Property(int, 1)
    blast_extra_args = Property(str, '-outfmt "6 length pident qseqid sseqid sseq qframe sframe"')

    append_timestamp = Property(bool, False)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self._update_num_threads_default()

        self.binder.bind(self.input_queries.properties.parent_path, self.properties.output_path)

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.input_queries.properties.ready,
            self.properties.input_database_path,
            self.properties.input_nucleotides_path,
            self.properties.output_path,
            self.properties.blast_method,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if not self.input_queries.ready:
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
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        self.exec(
            process.execute,
            work_dir=work_dir,
            input_queries=self.input_queries.get_all_paths(),
            input_database_path=self.input_database_path,
            input_nucleotides_path=self.input_nucleotides_path,
            output_path=self.output_path,
            blast_evalue=self.blast_evalue or self.properties.blast_evalue.default,
            blast_num_threads=self.blast_num_threads or self.properties.blast_num_threads.default,
            append_timestamp=self.append_timestamp,
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
            self.input_queries.open(path)
