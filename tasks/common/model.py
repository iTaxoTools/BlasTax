from PySide6 import QtCore

from itaxotools.taxi_gui.loop import ReportDone
from itaxotools.taxi_gui.model.tasks import TaskModel

from ..common.types import Results


class BlastTaskModel(TaskModel):
    reportResults = QtCore.Signal(str, Results)

    def onDone(self, report: ReportDone):
        self.reportResults.emit(self.task_name, report.result)
        self.busy = False
