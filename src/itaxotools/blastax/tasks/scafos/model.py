from datetime import datetime
from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BatchQueryModel, BlastTaskModel
from . import process, title
from .types import AmalgamationMethodTexts, TagMethodTexts


class Model(BlastTaskModel):
    task_name = title

    input_sequences = Property(BatchQueryModel, Instance)
    output_path = Property(Path, Path())

    tag_method = Property(TagMethodTexts, TagMethodTexts.SpeciesBeforeFirstUnderscore)
    amalgamation_method = Property(AmalgamationMethodTexts, AmalgamationMethodTexts.ByMaxLength)
    save_reports = Property(bool, False)
    fuse_ambiguous = Property(bool, True)
    outlier_factor = Property(float, 1.5)

    append_timestamp = Property(bool, False)
    append_configuration = Property(bool, True)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.input_sequences.set_globs(["fa", "fas", "fasta", "fq", "fastq", "ali"])

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
            input_paths=self.input_sequences.get_all_paths(),
            output_path=self.output_path,
            tag_method=self.tag_method,
            amalgamation_method=self.amalgamation_method,
            save_reports=self.save_reports,
            fuse_ambiguous=self.fuse_ambiguous,
            outlier_factor=self.outlier_factor,
            append_timestamp=self.append_timestamp,
            append_configuration=self.append_configuration,
        )

    def open(self, path: Path):
        self.input_sequences.open(path)
