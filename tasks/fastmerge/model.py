from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BatchQueryModel, BlastTaskModel
from . import process, title
from .types import FormatGroup


class Model(BlastTaskModel):
    task_name = title

    input_sequences = Property(BatchQueryModel, Instance)
    output_path = Property(Path, Path())

    format_group = Property(FormatGroup, FormatGroup.all)
    pattern_identifier = Property(str, "")
    pattern_sequence = Property(str, "")

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.input_sequences.set_globs([])

        self.subtask_init = SubtaskModel(self, bind_busy=False)
        self.input_sequences.batch_mode = True

        for handle in [
            self.input_sequences.properties.ready,
            self.properties.output_path,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if not self.input_sequences.ready:
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
            format_group=self.format_group,
            pattern_identifier=self.pattern_identifier,
            pattern_sequence=self.pattern_sequence,
        )

    def open(self, path: Path):
        self.input_sequences.open(path)
