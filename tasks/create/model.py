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
    database_type = Property(str, "nucl")

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = False
        self.can_save = False

        for handle in [
            self.properties.input_path,
            self.properties.output_path,
            self.properties.database_name,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

    def isReady(self):
        if self.input_path == Path():
            return False
        if self.output_path == Path():
            return False
        if not self.database_name:
            return False
        return True

    def start(self):
        super().start()

        print(self.input_path)
        print(self.output_path)
        print(self.database_name)
        print(self.database_type)

        self.exec(
            process.execute,
        )

    def onDone(self, report):
        time_taken = human_readable_seconds(report.result.seconds_taken)
        self.notification.emit(Notification.Info(f"{self.name} completed successfully!\nTime taken: {time_taken}."))

        self.busy = False
