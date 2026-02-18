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
from .types import OperationMode


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

    operation_mode = Property(OperationMode, OperationMode.database_to_fasta)
    show_input_database = Property(bool, False)
    show_input_taxdb = Property(bool, False)
    show_output_path = Property(bool, False)
    show_input_fasta_path = Property(bool, False)
    show_output_fasta_path = Property(bool, False)
    show_outfmt = Property(bool, False)

    input_database_path = Property(Path, Path())
    output_path = Property(Path, Path())
    output_placeholder = Property(str, "Output file")
    input_fasta_path = Property(Path, Path())
    output_fasta_path = Property(Path, Path())

    blast_outfmt = Property(str, ">%a [taxid=%T] [organism=%S]\\n%s\\n")

    blast_taxdb_path = Property(Path, Path())

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = False

        self.subtask_init = SubtaskModel(self, bind_busy=False)
        self.subtask_check = CheckInfoModel(self, bind_busy=True)

        self.binder.bind(self.properties.operation_mode, self._update_shown_cards)
        self.binder.bind(self.properties.input_database_path, self._update_output_paths)
        self.binder.bind(self.properties.input_fasta_path, self._update_output_paths)

        for handle in [
            self.properties.operation_mode,
            self.properties.input_database_path,
            self.properties.output_path,
            self.properties.input_fasta_path,
            self.properties.output_fasta_path,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.start(process.initialize)

    def _update_output_paths(self) -> Path:
        print("_update_output_paths")
        match self.operation_mode:
            case OperationMode.database_to_fasta:
                self.output_placeholder = "Exported sequences as FASTA file"
                input_path = self.input_database_path
                if input_path == Path():
                    self.output_path = Path()
                    return
                output_path = input_path.with_stem(input_path.stem + "_exported")
                self.output_path = output_path.with_suffix(".fasta")
            case OperationMode.taxid_map_from_database:
                self.output_placeholder = "Extracted taxID map as Tabfile"
                input_path = self.input_database_path
                if input_path == Path():
                    self.output_path = Path()
                    return
                output_path = input_path.with_stem(input_path.stem + "_taxid_map")
                self.output_path = output_path.with_suffix(".tsv")
            case OperationMode.taxid_map_from_fasta:
                self.output_placeholder = "Extracted taxID map as Tabfile"
                input_path = self.input_fasta_path
                if input_path == Path():
                    self.output_fasta_path = Path()
                    return
                output_path = input_path.with_stem(input_path.stem + "_no_tags")
                self.output_fasta_path = output_path.with_suffix(".fasta")
                output_path = input_path.with_stem(input_path.stem + "_taxid_map")
                self.output_path = output_path.with_suffix(".tsv")
            case _:
                self.output_path = Path()

    def _update_shown_cards(self, mode: OperationMode):
        match mode:
            case OperationMode.database_to_fasta:
                self.show_input_database = True
                self.show_input_taxdb = True
                self.show_output_path = True
                self.show_input_fasta_path = False
                self.show_output_fasta_path = False
                self.show_outfmt = True
            case OperationMode.database_check_taxid:
                self.show_input_database = True
                self.show_input_taxdb = False
                self.show_output_path = False
                self.show_input_fasta_path = False
                self.show_output_fasta_path = False
                self.show_outfmt = False
            case OperationMode.taxid_map_from_database:
                self.show_input_database = True
                self.show_input_taxdb = False
                self.show_output_path = True
                self.show_input_fasta_path = False
                self.show_output_fasta_path = False
                self.show_outfmt = False
            case OperationMode.taxid_map_from_fasta:
                self.show_input_database = False
                self.show_input_taxdb = False
                self.show_output_path = True
                self.show_input_fasta_path = True
                self.show_output_fasta_path = True
                self.show_outfmt = False
            case _:
                self.show_input_database = False
                self.show_input_taxdb = False
                self.show_output_path = False
                self.show_input_fasta_path = False
                self.show_output_fasta_path = False
                self.show_outfmt = False
        self._update_output_paths()

    def isReady(self):
        if self.show_input_database and self.input_database_path == Path():
            return False
        if self.show_output_path and self.output_path == Path():
            return False
        if self.show_input_fasta_path and self.input_fasta_path == Path():
            return False
        if self.show_output_fasta_path and self.output_fasta_path == Path():
            return False
        return True

    def start(self):
        super().start()
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        match self.operation_mode:
            case OperationMode.database_to_fasta:
                self.exec(
                    process.database_to_fasta,
                    work_dir=work_dir,
                    input_database_path=self.input_database_path,
                    output_path=self.output_path,
                    blast_outfmt=self.blast_outfmt or self.properties.blast_outfmt.default,
                    blast_taxdb_path=self.blast_taxdb_path if self.blast_taxdb_path != Path() else None,
                )
            case OperationMode.database_check_taxid:
                self.exec(
                    process.database_check_taxid,
                    work_dir=work_dir,
                    input_database_path=self.input_database_path,
                )
            case OperationMode.taxid_map_from_database:
                self.exec(
                    process.database_to_fasta,
                    work_dir=work_dir,
                    input_database_path=self.input_database_path,
                    output_path=self.output_path,
                    blast_outfmt="%a\\t%T",
                    blast_taxdb_path=None,
                )
            case OperationMode.taxid_map_from_fasta:
                self.exec(
                    process.taxid_map_from_fasta,
                    input_fasta_path=self.input_fasta_path,
                    output_fasta_path=self.output_fasta_path,
                    output_map_path=self.output_path,
                )

    def onDone(self, report: ReportDone):
        if self.operation_mode == OperationMode.database_check_taxid:
            if report.result is None:
                self.notification.emit(Notification.Error("Could not read taxonomy IDs from the database."))
            elif report.result:
                self.notification.emit(Notification.Info("Database DOES contain taxonomy ID mappings."))
            else:
                self.notification.emit(Notification.Warn("Database does NOT contain taxonomy ID mappings."))
            self.busy = False
            return

        super().onDone(report)

    def outfmt_restore_defaults(self):
        self.blast_outfmt = self.properties.blast_outfmt.default

    def open(self, path: Path):
        if self.show_input_database:
            if db := get_database_index_from_path(path):
                self.input_database_path = db
        else:
            self.input_fasta_path = path
