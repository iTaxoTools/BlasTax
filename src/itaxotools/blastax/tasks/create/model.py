from datetime import datetime
from pathlib import Path

from itaxotools.blastax.utils import make_str_blast_safe
from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BatchQueryModel, BlastTaskModel
from . import process, title


class Model(BlastTaskModel):
    task_name = title.replace(" ", "_")

    input = Property(BatchQueryModel, Instance)
    output_path = Property(Path, Path())
    database_type = Property(str, "nucl")
    database_name = Property(str, "")
    parse_ids = Property(bool, False)
    taxid_map_path = Property(Path, Path())

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.input.set_globs(["fa", "fas", "fasta"])

        self.binder.bind(self.input.properties.parent_path, self.properties.output_path)
        self.binder.bind(
            self.input.properties.query_path, self.properties.database_name, lambda x: make_str_blast_safe(x.stem)
        )

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.input.properties.ready,
            self.input.properties.batch_mode,
            self.properties.output_path,
            self.properties.database_name,
            self.properties.parse_ids,
            self.properties.taxid_map_path,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if not self.input.ready:
            return False
        if self.output_path == Path():
            return False
        if not self.input.batch_mode and not self.database_name:
            return False
        if self.parse_ids and self.taxid_map_path == Path():
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
            input_paths=self.input.get_all_paths(),
            output_path=self.output_path,
            type=self.database_type,
            name=self.database_name,
            taxid_map_path=self.taxid_map_path if self.parse_ids else Path(),
        )

    def open(self, path: Path):
        self.input.open(path)
