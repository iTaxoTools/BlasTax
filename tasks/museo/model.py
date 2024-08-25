import multiprocessing
from datetime import datetime
from pathlib import Path

from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BlastTaskModel
from ..common.types import BlastMethod
from ..common.utils import get_database_index_from_path
from . import process, title


class Model(BlastTaskModel):
    task_name = title

    input_query_path = Property(Path, Path())
    input_database_path = Property(Path, Path())
    output_path = Property(Path, Path())

    pident_threshold = Property(float, 90.000)
    retrieve_original = Property(bool, False)

    blast_method = Property(BlastMethod, BlastMethod.blastn)
    blast_evalue = Property(float, 1e-5)
    blast_num_threads = Property(int, 1)
    blast_extra_args = Property(str, '-outfmt "6 qseqid sseqid sacc stitle pident qseq"')

    append_timestamp = Property(bool, False)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self._update_num_threads_default()

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
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        self.exec(
            process.execute,
            work_dir=work_dir,
            input_query_path=self.input_query_path,
            input_database_path=self.input_database_path,
            output_path=self.output_path,
            blast_evalue=self.blast_evalue or self.properties.blast_evalue.default,
            blast_num_threads=self.blast_num_threads or self.properties.blast_num_threads.default,
            pident_threshold=self.pident_threshold,
            retrieve_original=self.retrieve_original,
            append_timestamp=self.append_timestamp,
        )

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
        if db := get_database_index_from_path(path):
            self.input_database_path = db
        else:
            self.input_query_path = path
            self.output_path = path.parent
