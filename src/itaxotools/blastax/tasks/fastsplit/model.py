from pathlib import Path

from itaxotools.blastax.fastsplit import parse_size
from itaxotools.blastax.fastutils import make_template
from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BlastTaskModel
from . import process, title
from .types import FileFormat, SplitOption


class Model(BlastTaskModel):
    task_name = title

    input_path = Property(Path, Path())
    output_path = Property(Path, Path())

    filename_template = Property(str, "")
    output_format = Property(FileFormat, FileFormat.fasta)
    split_option = Property(SplitOption, SplitOption.max_size)

    split_n = Property(int, 4)
    max_size = Property(str, "1k")
    pattern_available = Property(bool, True)
    pattern_identifier = Property(str, "")
    pattern_sequence = Property(str, "")
    compress = Property(bool, False)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.binder.bind(self.properties.input_path, self.properties.output_path, lambda p: p.parent)
        self.binder.bind(
            self.properties.input_path, self.properties.filename_template, lambda p: self.get_template_from_path(p)
        )
        self.binder.bind(
            self.properties.output_format, self.properties.pattern_available, lambda x: x != FileFormat.text
        )

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.properties.input_path,
            self.properties.output_path,
            self.properties.filename_template,
            self.properties.output_format,
            self.properties.split_option,
            self.properties.split_n,
            self.properties.max_size,
            self.properties.pattern_identifier,
            self.properties.pattern_sequence,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if self.input_path == Path():
            return False
        if self.output_path == Path():
            return False
        if not self.filename_template:
            return False
        if not self.check_options_valid():
            return False
        return True

    @staticmethod
    def get_template_from_path(path: Path):
        if path == Path():
            return ""
        return make_template(path.name)

    def get_safe_max_size(self) -> int:
        max_size = self.max_size or self.properties.max_size.default
        try:
            return parse_size(max_size)
        except Exception:
            return None

    def check_options_valid(self) -> bool:
        if self.output_format == FileFormat.text:
            if self.split_option not in [SplitOption.max_size, SplitOption.split_n]:
                return False
        if self.split_option == SplitOption.max_size:
            if not self.get_safe_max_size():
                return False
        return True

    def get_options_dict(self) -> dict:
        max_size = None
        split_n = None
        pattern_identifier = None
        pattern_sequence = None

        match self.split_option:
            case SplitOption.max_size:
                max_size = self.get_safe_max_size()
            case SplitOption.split_n:
                split_n = self.split_n
            case SplitOption.pattern_identifier:
                pattern_identifier = self.pattern_identifier
            case SplitOption.pattern_sequence:
                pattern_sequence = self.pattern_sequence

        return dict(
            max_size=max_size,
            split_n=split_n,
            pattern_identifier=pattern_identifier,
            pattern_sequence=pattern_sequence,
        )

    def start(self):
        super().start()

        self.exec(
            process.execute,
            input_path=self.input_path,
            output_path=self.output_path,
            filename_template=self.filename_template,
            output_format=self.output_format.key,
            compress=self.compress,
            **self.get_options_dict(),
        )

    def open(self, path: Path):
        self.input_path = path
