from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BatchQueryModel, BlastTaskModel
from . import process, title
from .types import RemovalMode


class Model(BlastTaskModel):
    task_name = title

    input_paths = Property(BatchQueryModel, Instance)
    output_path = Property(Path, Path())

    option_mode = Property(RemovalMode, RemovalMode.trim_after_stop)
    option_frame = Property(int, 1)
    option_code = Property(int, 1)
    option_cutoff = Property(int, 15)
    option_log = Property(bool, True)

    append_timestamp = Property(bool, False)
    append_configuration = Property(bool, True)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.input_paths.batch_mode = True
        self.input_paths.set_globs(["fa", "fas", "fasta"])

        self.binder.bind(self.input_paths.properties.parent_path, self.properties.output_path)

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.input_paths.properties.ready,
            self.properties.output_path,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if not self.input_paths.ready:
            return False
        if self.output_path == Path():
            return False
        return True

    def start(self):
        super().start()

        self.exec(
            process.execute,
            input_paths=self.input_paths.get_all_paths(),
            output_dir=self.output_path,
            mode=self.option_mode,
            frame=self.option_frame,
            code=self.option_code,
            cutoff=self.option_cutoff,
            log=self.option_log,
            append_timestamp=self.append_timestamp,
            append_configuration=self.append_configuration,
        )

    def open(self, path: Path):
        self.input_paths.open(path)
