from pathlib import Path

from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BlastTaskModel
from . import process, title
from .types import MatchingRule


class Model(BlastTaskModel):
    task_name = title

    input_path = Property(Path, Path())
    output_path = Property(Path, Path())

    matching_rule = Property(MatchingRule, MatchingRule.word)
    matching_characters = Property(int, 4)
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

    def get_regex_from_properties(self):
        if self.matching_rule == MatchingRule.regex:
            return self.matching_regex or self.properties.matching_regex.default
        elif self.matching_rule == MatchingRule.characters:
            return r"^(.{" + str(self.matching_characters) + r"})"
        elif self.matching_rule == MatchingRule.word:
            return r"^([^\s_]+)"

    def start(self):
        super().start()

        self.exec(
            process.execute,
            input_path=self.input_path,
            output_path=self.output_path,
            discard_duplicates=self.discard_duplicates,
            matching_regex=self.get_regex_from_properties(),
        )

    def open(self, path: Path):
        self.input_path = path
        self.output_path = path
