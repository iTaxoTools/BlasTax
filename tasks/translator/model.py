from pathlib import Path

from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BlastTaskModel
from . import process, title
from .types import ReadingFrame, TranslationMode


class Model(BlastTaskModel):
    task_name = title

    input_path = Property(Path, Path())
    output_path = Property(Path, Path())

    output_filename = Property(str, "")
    nucleotide_filename = Property(str, "nucleotids")
    log_filename = Property(str, "translator.log")

    option_mode = Property(TranslationMode, TranslationMode.cds)
    option_frame = Property(ReadingFrame, None)
    option_code = Property(int, None)
    option_stop = Property(bool, False)
    option_log = Property(bool, True)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.binder.bind(self.properties.input_path, self.properties.output_path, lambda p: p.parent)
        self.binder.bind(
            self.properties.input_path, self.properties.output_filename, lambda p: self.get_template_from_path(p)
        )
        self.binder.bind(
            self.properties.output_filename,
            self.properties.log_filename,
            lambda f: Path(f).with_suffix(".log").name if f else "",
        )

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.properties.input_path,
            self.properties.output_path,
            self.properties.output_filename,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if self.input_path == Path():
            return False
        if self.output_path == Path():
            return False
        if not self.output_filename:
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

        self.exec(
            process.execute,
            input_path=self.input_path,
            output_path=self.output_path / self.output_filename,
            log_path=self.output_path / self.log_filename if self.option_log else None,
            nucleotide_path=self.output_path / self.nucleotide_filename
            if self.option_mode == TranslationMode.transscript
            else None,
            input_type=str(self.option_mode),
            stop=str(self.option_stop),
            frame=str(self.option_frame),
            code=str(self.option_code),
        )

    def open(self, path: Path):
        self.input_path = path
