import multiprocessing
from pathlib import Path

from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.model.tasks import TaskModel
from itaxotools.taxi_gui.types import Notification
from itaxotools.taxi_gui.utility import human_readable_seconds

from ..common.types import BlastMethod
from . import process, title


class Model(TaskModel):
    task_name = title

    batch_mode = Property(bool, False)
    input_query_path = Property(Path, Path())
    input_query_list = Property(object, None)
    input_database_path = Property(Path, Path())
    input_nucleotides_path = Property(Path, Path())
    output_path = Property(Path, Path())

    blast_method = Property(BlastMethod, BlastMethod.blastn)
    blast_evalue = Property(float, 1e-5)
    blast_num_threads = Property(int, 1)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = False
        self.can_save = False

        self._update_num_threads_default()

    def isReady(self):
        return True

    def start(self):
        super().start()

        print(f"{self.batch_mode=}")
        print(f"{self.input_query_path=}")
        print(f"{self.input_database_path=}")
        print(f"{self.input_nucleotides_path=}")
        print(f"{self.output_path=}")
        print(f"{self.blast_method.executable=}")
        print(f"{self.blast_evalue=}")
        print(f"{self.blast_num_threads=}")

        self.exec(
            process.execute,
        )

    def onDone(self, report):
        time_taken = human_readable_seconds(report.result.seconds_taken)
        self.notification.emit(Notification.Info(f"{self.name} completed successfully!\nTime taken: {time_taken}."))

        self.busy = False

    def _update_num_threads_default(self):
        cpus = multiprocessing.cpu_count()
        property = self.properties.blast_num_threads
        setattr(property._parent, Property.key_default(property._key), cpus)
        property.set(cpus)
