from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BatchQueryModel, BlastTaskModel
from . import process, title
from .types import Direction


class Model(BlastTaskModel):
    task_name = title

    input_sequences = Property(BatchQueryModel, Instance)
    output_path = Property(Path, Path())

    sanitize = Property(bool, True)
    preserve_separators = Property(bool, False)
    auto_increment = Property(bool, True)

    trim = Property(bool, True)
    trim_direction = Property(Direction, Direction.End)
    trim_max_length = Property(int, 50)

    add = Property(bool, False)
    add_direction = Property(Direction, Direction.End)
    add_text = Property(str, "")

    replace = Property(bool, False)
    replace_source = Property(str, "")
    replace_target = Property(str, "")

    ali = Property(bool, False)
    fixseqspaces = Property(bool, True)
    fixseqasterisks = Property(bool, True)
    fixaliseparator = Property(bool, True)

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
            self.properties.add,
            self.properties.add_text,
            self.properties.replace,
            self.properties.replace_source,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if not self.input_sequences.ready:
            return False
        if self.output_path == Path():
            return False
        if self.add and not self.add_text:
            return False
        if self.replace and not self.replace_source:
            return False
        return True

    def start(self):
        super().start()
        self.exec(
            process.execute,
            input_paths=self.input_sequences.get_all_paths(),
            output_path=self.output_path,
            sanitize=self.sanitize,
            preserve_separators=self.preserve_separators,
            auto_increment=self.auto_increment,
            trim=self.trim,
            trim_direction=str(self.trim_direction),
            trim_max_length=self.trim_max_length,
            add=self.add,
            add_direction=str(self.add_direction),
            add_text=self.add_text,
            replace=self.replace,
            replace_source=self.replace_source,
            replace_target=self.replace_target,
            fixseqspaces=self.ali and self.fixseqspaces,
            fixseqasterisks=self.ali and self.fixseqasterisks,
            fixaliseparator=self.ali and self.fixaliseparator,
            append_timestamp=self.append_timestamp,
        )

    def open(self, path: Path):
        self.input_sequences.open(path)
