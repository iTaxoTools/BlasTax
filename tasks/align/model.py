from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.model.tasks import TaskModel
from itaxotools.taxi_gui.types import Notification
from itaxotools.taxi_gui.utility import human_readable_seconds

from ..common.types import BlastMethod
from . import process, title


class Model(TaskModel):
    task_name = title

    batch_mode = Property(bool, False)

    blast_method = Property(BlastMethod, BlastMethod.blastn)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = False
        self.can_save = False

    def isReady(self):
        return True

    def start(self):
        super().start()

        print(f"{self.batch_mode=}")
        print(f"{self.blast_method.executable=}")

        self.exec(
            process.execute,
        )

    def onDone(self, report):
        time_taken = human_readable_seconds(report.result.seconds_taken)
        self.notification.emit(Notification.Info(f"{self.name} completed successfully!\nTime taken: {time_taken}."))

        self.busy = False
