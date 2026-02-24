from pathlib import Path

from itaxotools.common.bindings import Property

from ..common.model import BlastTaskModel
from . import process, title


class Model(BlastTaskModel):
    task_name = title.replace(" ", "_")

    output_path = Property(Path, Path())

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = False
        self.can_save = False

        self.binder.bind(self.properties.output_path, self.checkReady)
        self.checkReady()

    def isReady(self):
        if self.output_path == Path():
            return False
        return True

    def start(self):
        super().start()
        self.exec(
            process.execute,
            output_path=self.output_path,
        )
