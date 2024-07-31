from pathlib import Path

from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.model.tasks import TaskModel
from itaxotools.taxi_gui.types import Notification
from itaxotools.taxi_gui.utility import human_readable_seconds

from . import process, title


class Model(TaskModel):
    task_name = title

    input_path = Property(Path, Path())
    output_path = Property(Path, Path())
    database_name = Property(str, "")

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = False
        self.can_save = False

    def isReady(self):
        return True

    def start(self):
        super().start()

        print(self.input_path)
        print(self.output_path)
        print(self.database_name)

        self.exec(
            process.execute,
        )

    def onDone(self, report):
        time_taken = human_readable_seconds(report.result.seconds_taken)
        self.notification.emit(Notification.Info(f"{self.name} completed successfully!\nTime taken: {time_taken}."))

        self.busy = False
