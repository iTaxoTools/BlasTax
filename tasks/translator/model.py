from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BatchQueryModel, BlastTaskModel
from . import process, title
from .types import TranslationMode


class Model(BlastTaskModel):
    task_name = title

    input_paths = Property(BatchQueryModel, Instance)
    output_path = Property(Path, Path())

    output_filename = Property(str, "")
    nucleotides_filename = Property(str, "nucleotids")
    log_filename = Property(str, "translator.log")

    option_mode = Property(TranslationMode, TranslationMode.cds)
    option_frame = Property(str, "autodetect")
    option_code = Property(int, 1)
    option_log = Property(bool, True)
    option_nucleotides = Property(bool, True)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.binder.bind(self.input_paths.properties.parent_path, self.properties.output_path)
        self.binder.bind(
            self.input_paths.properties.query_path,
            self.properties.output_filename,
            lambda p: self.get_template_from_path(p),
        )
        self.binder.bind(
            self.properties.output_filename,
            self.properties.log_filename,
            lambda f: Path(f).with_suffix(".log").name if f else "",
        )
        self.binder.bind(
            self.properties.output_filename,
            self.properties.nucleotides_filename,
            lambda f: Path(f).with_stem(Path(f).stem + "_orf_nt").name if f else "",
        )

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.input_paths.properties.ready,
            self.properties.output_path,
            self.properties.output_filename,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if not self.input_paths.ready:
            return False
        if self.output_path == Path():
            return False
        if not self.input_paths.batch_mode and not self.output_filename:
            return False
        return True

    @staticmethod
    def get_template_from_path(path: Path) -> str:
        if path == Path():
            return ""
        path = path.with_stem(path.stem + "_aa")
        path = path.with_suffix(".fasta")
        return path.name

    def start(self):
        super().start()

        if self.input_paths.batch_mode:
            self.exec(
                process.execute_batch,
                input_paths=self.input_paths.get_all_paths(),
                output_dir=self.output_path,
                write_logs=self.option_log,
                write_nucleotides=self.option_nucleotides,
                input_type=str(self.option_mode),
                frame=str(self.option_frame),
                code=str(self.option_code),
            )
        else:
            self.exec(
                process.execute,
                input_path=self.input_paths.query_path,
                output_path=self.output_path / self.output_filename,
                log_path=self.output_path / self.log_filename if self.option_log else None,
                nucleotide_path=self.output_path / self.nucleotides_filename
                if self.option_mode == TranslationMode.transcript and self.option_nucleotides
                else None,
                input_type=str(self.option_mode),
                frame=str(self.option_frame),
                code=str(self.option_code),
            )

    def open(self, path: Path):
        self.input_paths.open(path)
