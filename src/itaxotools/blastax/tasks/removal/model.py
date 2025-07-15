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

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.input_paths.batch_mode = True

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
            output_path=self.output_path,
            mode=self.option_mode,
            frame=int(self.option_frame),
            code=int(self.option_code),
        )

    def open(self, path: Path):
        self.input_paths.open(path)
