from pathlib import Path

from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel, TaskModel
from itaxotools.taxi_gui.types import Notification
from itaxotools.taxi_gui.utility import human_readable_seconds

from . import process, title


class Model(TaskModel):
    task_name = title

    input_path = Property(Path, Path())
    output_path = Property(Path, Path())
    database_type = Property(str, "nucl")
    database_name = Property(str, "")

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = False
        self.can_save = False

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.properties.input_path,
            self.properties.output_path,
            self.properties.database_name,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

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

        self.exec(
            process.execute,
            input_path=str(self.input_path),
            output_path=str(self.output_path),
            type=self.database_type,
            name=self.database_name,
        )

    def onDone(self, report):
        time_taken = human_readable_seconds(report.result.seconds_taken)
        self.notification.emit(Notification.Info(f"Database created successfully!\nTime taken: {time_taken}."))

        self.busy = False
