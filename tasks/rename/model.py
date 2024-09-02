from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BatchQueryModel, BlastTaskModel
from . import process, title
from .types import Position


class Model(BlastTaskModel):
    task_name = title

    input_sequences = Property(BatchQueryModel, Instance)
    output_path = Property(Path, Path())

    sanitize = Property(bool, True)
    auto_increment = Property(bool, True)

    trim = Property(bool, True)
    trim_position = Property(Position, Position.End)
    trim_max_char = Property(int, 50)

    add = Property(bool, True)
    add_position = Property(Position, Position.End)
    add_text = Property(str, "_")

    append_timestamp = Property(bool, False)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.input_sequences.set_globs(["fa", "fas", "fasta"])
        self.binder.bind(self.input_sequences.properties.parent_path, self.properties.output_path)

        self.subtask_init = SubtaskModel(self, bind_busy=False)

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
            input_paths=self.input_sequences.get_all_paths(),
            output_path=self.output_path,
            sanitize=self.sanitize,
            auto_increment=self.auto_increment,
            trim=self.trim,
            trim_position=str(self.trim_position),
            trim_max_char=self.trim_max_char,
            add=self.add,
            add_position=str(self.add_position),
            add_text=self.add_text,
            append_timestamp=self.append_timestamp,
        )

    def open(self, path: Path):
        self.input_sequences.open(path)
