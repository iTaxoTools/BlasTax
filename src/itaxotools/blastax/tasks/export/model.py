from PySide6 import QtCore

from datetime import datetime
from pathlib import Path

from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel
from itaxotools.taxi_gui.threading import ReportDone
from itaxotools.taxi_gui.types import Notification

from ..common.model import BlastTaskModel
from ..common.utils import get_database_index_from_path
from . import process, title


class CheckInfoModel(SubtaskModel):
    has_taxids = QtCore.Signal(object)

    def start(self, work_dir: Path, input_database_path: Path):
        self.busy = True
        self.exec(process.check, work_dir, input_database_path)

    def onDone(self, report: ReportDone):
        self.has_taxids.emit(report.result)
        if report.result is None:
            self.notification.emit(Notification.Warn("Could not read taxonomy IDs from the database."))
        elif report.result:
            self.notification.emit(Notification.Info("Database contains taxonomy ID mappings."))
        else:
            self.notification.emit(Notification.Warn("Database does not contain taxonomy ID mappings."))
        self.busy = False


class Model(BlastTaskModel):
    task_name = title.replace(" ", "_")

    input_database_path = Property(Path, Path())
    output_path = Property(Path, Path())

    has_taxids = Property(bool | None, None)
    blast_outfmt = Property(str, ">%a [taxid=%T]\\n%s\\n")

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.subtask_init = SubtaskModel(self, bind_busy=False)
        self.subtask_check = CheckInfoModel(self, bind_busy=True)

        self.binder.bind(self.subtask_check.has_taxids, self.properties.has_taxids)
        self.binder.bind(self.properties.input_database_path, self.properties.has_taxids, lambda x: None)
        self.binder.bind(
            self.properties.input_database_path, self.properties.output_path, lambda x: self._get_output_path(x)
        )

        for handle in [
            self.properties.input_database_path,
            self.properties.output_path,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    @staticmethod
    def _get_output_path(input_path: Path) -> Path:
        if input_path == Path():
            return Path()
        output_path = input_path.with_stem(input_path.stem + "_exported")
        output_path = output_path.with_suffix(".fasta")
        return output_path

    def isReady(self):
        if self.input_database_path == Path():
            return False
        if self.output_path == Path():
            return False
        return True

    def start(self):
        super().start()
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        self.exec(
            process.execute,
            work_dir=work_dir,
            input_database_path=self.input_database_path,
            output_path=self.output_path,
            blast_outfmt=self.blast_outfmt or self.properties.blast_outfmt.default,
        )

    def outfmt_restore_defaults(self):
        self.blast_outfmt = self.properties.blast_outfmt.default

    def open(self, path: Path):
        if db := get_database_index_from_path(path):
            self.input_database_path = db

    def check_taxids(self):
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        self.subtask_check.start(
            work_dir=work_dir,
            input_database_path=self.input_database_path,
        )
