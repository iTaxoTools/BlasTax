from pathlib import Path

from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BlastTaskModel
from . import process, title


class Model(BlastTaskModel):
    task_name = title

    input_path = Property(Path, Path())
    output_path = Property(Path, Path())

    matching_regex = Property(str, r"^(\d+)")
    discard_duplicates = Property(bool, True)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.properties.input_path,
            self.properties.output_path,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if self.input_path == Path():
            return False
        if self.output_path == Path():
            return False
        return True

    def start(self):
        super().start()

        self.exec(
            process.execute,
            input_path=self.input_path,
            output_path=self.output_path,
            discard_duplicates=self.discard_duplicates,
            matching_regex=self.matching_regex,
        )

    def open(self, path: Path):
        self.input_path = path
        self.output_path = path
