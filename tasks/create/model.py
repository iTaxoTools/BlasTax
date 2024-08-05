from pathlib import Path

from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BlastTaskModel
from . import process, title


class Model(BlastTaskModel):
    task_name = title

    input_path = Property(Path, Path())
    output_path = Property(Path, Path())
    database_type = Property(str, "nucl")
    database_name = Property(str, "")

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.properties.input_path,
            self.properties.output_path,
            self.properties.database_name,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if self.input_path == Path():
            return False
        if self.output_path == Path():
            return False
        if not self.database_name:
            return False
        return True

    def start(self):
        super().start()

        self.exec(
            process.execute,
            input_path=self.input_path,
            output_path=self.output_path,
            type=self.database_type,
            name=self.database_name,
        )

    def open(self, path: Path):
        self.input_path = path
        self.output_path = path.parent
        self.database_name = path.stem
