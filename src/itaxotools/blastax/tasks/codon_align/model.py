from datetime import datetime
from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BatchQueryModel, BlastTaskModel
from ..mafft.types import AdjustDirection, AlignmentStrategy
from . import process, title


class Model(BlastTaskModel):
    task_name = title

    input_sequences = Property(BatchQueryModel, Instance)
    output_path = Property(Path, Path())

    codon_table = Property(int, 1)
    strategy = Property(AlignmentStrategy, AlignmentStrategy.Auto)
    adjust_direction = Property(AdjustDirection, AdjustDirection.No)

    append_timestamp = Property(bool, False)
    append_configuration = Property(bool, True)

    def __init__(self, name=None):
        super().__init__(name, daemon=False)
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
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        self.exec(
            process.execute,
            work_dir=work_dir,
            input_paths=self.input_sequences.get_all_paths(),
            output_path=self.output_path,
            codon_table=self.codon_table,
            strategy=self.strategy,
            adjust_direction=self.adjust_direction,
            append_timestamp=self.append_timestamp,
            append_configuration=self.append_configuration,
        )

    def open(self, path: Path):
        self.input_sequences.open(path)
