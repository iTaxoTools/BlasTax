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
    task_name = title.replace(" ", "_")

    input_queries = Property(BatchQueryModel, Instance)
    input_database_path = Property(Path, Path())
    output_path = Property(Path, Path())

    blast_method = Property(BlastMethod, BlastMethod.blastn)
    blast_evalue = Property(float, 1e-5)
    blast_num_threads = Property(int, 1)
    blast_extra_args = Property(str, '-outfmt "6 qseqid sseqid pident bitscore length staxids"')
    blast_taxdb_path = Property(Path, Path())

    taxid_mode_text = Property(bool, True)
    taxid_text = Property(str, "")
    taxid_path = Property(Path, Path())
    taxid_negative = Property(bool, False)
    taxid_expand = Property(bool, True)

    filter_pident = Property(bool, True)
    filter_bitscore = Property(bool, False)
    filter_length = Property(bool, False)
    threshold_pident = Property(float, 97.0)
    threshold_bitscore = Property(float, 0.0)
    threshold_length = Property(float, 0.0)

    append_timestamp = Property(bool, False)
    append_configuration = Property(bool, True)

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
            self.properties.output_path,
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
        return True

    def start(self):
        super().start()
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        self.exec(
            process.execute,
            work_dir=work_dir,
            input_query_paths=self.input_queries.get_all_paths(),
            input_database_path=self.input_database_path,
            output_path=self.output_path,
            blast_method=self.blast_method.executable,
            blast_evalue=self.blast_evalue or self.properties.blast_evalue.default,
            blast_num_threads=self.blast_num_threads or self.properties.blast_num_threads.default,
            blast_taxdb_path=self.blast_taxdb_path if self.blast_taxdb_path != Path() else None,
            taxid_mode_text=self.taxid_mode_text,
            taxid_text=self.taxid_text,
            taxid_path=self.taxid_path if self.taxid_path != Path() else None,
            taxid_negative=self.taxid_negative,
            taxid_expand=self.taxid_expand,
            threshold_pident=self.threshold_pident if self.filter_pident else None,
            threshold_bitscore=self.threshold_bitscore if self.filter_bitscore else None,
            threshold_length=self.threshold_length if self.filter_length else None,
            append_timestamp=self.append_timestamp,
            append_configuration=self.append_configuration,
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
