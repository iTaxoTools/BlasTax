# -----------------------------------------------------------------------------
# Hapsolutely - Reconstruct haplotypes and produce genealogy graphs
# Copyright (C) 2023  Patmanidis Stefanos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

from PySide6 import QtCore

from itaxotools.common.bindings import Property
from itaxotools.taxi_gui.loop import ReportDone
from itaxotools.taxi_gui.model.tasks import SubtaskModel, TaskModel

from . import process, title


class VersionSubtaskModel(SubtaskModel):
    task_name = "VersionSubtask"

    done = QtCore.Signal(object)

    def onDone(self, version: str | None):
        self.done.emit(version)
        self.busy = False


class Model(TaskModel):
    task_name = title
    blast_version = Property(str, "checking version...")
    cutadapt_version = Property(str, "checking version...")

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = False
        self.can_save = False
        self.ready = False

        self.subtask_blast_version = VersionSubtaskModel(self, bind_busy=False)
        self.binder.bind(self.subtask_blast_version.done, self._handle_blast_version_done)
        self.subtask_blast_version.start(process.get_blast_version)

        self.subtask_cutadapt_version = VersionSubtaskModel(self, bind_busy=False)
        self.binder.bind(self.subtask_cutadapt_version.done, self._handle_cutadapt_version_done)
        self.subtask_cutadapt_version.start(process.get_cutadapt_version)

    def _handle_blast_version_done(self, report: ReportDone):
        version = report.result
        if version:
            self.blast_version = "v" + version
        else:
            self.blast_version = "could not find binaries!"

    def _handle_cutadapt_version_done(self, report: ReportDone):
        version = report.result
        if version:
            self.cutadapt_version = "v" + version
        else:
            self.cutadapt_version = "could not determine version!"
