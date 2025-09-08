from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BatchQueryModel, BlastTaskModel
from . import process, title


class Model(BlastTaskModel):
    task_name = title

    input_paths = Property(BatchQueryModel, Instance)
    output_dir = Property(Path, Path())

    adapters_a_enabled = Property(bool, False)
    adapters_g_enabled = Property(bool, False)
    adapters_a_list = Property(str, "")
    adapters_g_list = Property(str, "")

    append_timestamp = Property(bool, False)
    append_configuration = Property(bool, True)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.input_paths.batch_mode = True
        self.input_paths.set_globs(["fa", "fas", "fasta", "fq", "fastq"])

        self.binder.bind(self.input_paths.properties.parent_path, self.properties.output_dir)

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.input_paths.properties.ready,
            self.properties.output_dir,
            self.properties.adapters_a_enabled,
            self.properties.adapters_g_enabled,
            self.properties.adapters_a_list,
            self.properties.adapters_g_list,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if not self.input_paths.ready:
            return False
        if self.output_dir == Path():
            return False
        if not (self.adapters_a_enabled or self.adapters_g_enabled):
            return False
        if self.adapters_a_enabled and not self.adapters_a_list.strip():
            return False
        if self.adapters_g_enabled and not self.adapters_g_list.strip():
            return False
        return True

    def start(self):
        super().start()
        self.exec(
            process.execute,
            input_paths=self.input_paths.get_all_paths(),
            output_dir=self.output_dir,
            adapters_a=self.adapters_a_list if self.adapters_a_enabled else "",
            adapters_g=self.adapters_g_list if self.adapters_g_enabled else "",
            append_timestamp=self.append_timestamp,
            append_configuration=self.append_configuration,
        )

    def open(self, path: Path):
        self.input_paths.open(path)
