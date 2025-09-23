from PySide6 import QtCore, QtWidgets

import sys
from argparse import ArgumentParser
from contextlib import contextmanager
from pathlib import Path

from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.main import Main as _Main

from .blast import check_binaries_in_path, dump_user_blast_path, suggest_user_blast_path
from .download import get_blast, get_version


class DownloaderDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.version = "???"

        self.setWindowTitle(f"{app.config.title} - Downloading BLAST+")
        self.setModal(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.label = QtWidgets.QLabel("Preparing download...", self)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        layout.addWidget(self.label)

        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        layout.addWidget(self.progress)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(8)
        layout.addLayout(button_layout)

        self.cancel_btn = QtWidgets.QPushButton("Cancel", self)
        self.done_btn = QtWidgets.QPushButton("Done", self)
        self.done_btn.setEnabled(False)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.done_btn)

        self.cancel_btn.clicked.connect(self.reject)
        self.done_btn.clicked.connect(self.accept)

        self.worker = _DownloadWorker()
        self.worker.progress.connect(self.on_progress)
        self.worker.message.connect(self.on_message)
        self.worker.version.connect(self.on_version)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

        self.adjustSize()
        self.setFixedSize(self.sizeHint())
        self.setMinimumWidth(360)

    def on_progress(self, downloaded: int, total: int):
        if total > 0:
            percent = int(downloaded / total * 100)
            self.progress.setValue(percent)

    def on_message(self, msg: str):
        msg = msg.strip()
        if not msg:
            return
        elif msg.startswith("Total tarball size:"):
            size = msg.split(":", 1)[1].strip()
            self.label.setText(f"Downloading BLAST+ v{self.version} with total size: {size}...")
        elif msg.startswith("Tarball saved as"):
            self.label.setText("Extracting package...")
        elif msg.startswith("Extracted tarball"):
            self.label.setText("Finishing setup...")
        elif msg.startswith("Copied"):
            self.label.setText("Installing binaries...")
        elif msg.startswith("Done!"):
            self.label.setText("Download complete!")
        else:
            self.label.setText(msg)

    def on_version(self, version: str):
        self.version = version

    def on_finished(self):
        self.cancel_btn.setEnabled(False)
        self.done_btn.setEnabled(True)

    def reject(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        super().reject()


class _DownloadWorker(QtCore.QThread):
    progress = QtCore.Signal(int, int)
    message = QtCore.Signal(str)
    version = QtCore.Signal(str)

    def run(self):
        def handler(downloaded: int, total: int):
            self.progress.emit(downloaded, total)

        version = get_version()
        self.version.emit(version)

        path = suggest_user_blast_path()
        with self._redirect_stdout_to_signal():
            get_blast(target=path, version=version, handler=handler)
            dump_user_blast_path(path)

    @contextmanager
    def _redirect_stdout_to_signal(self):
        class StreamWrapper:
            def __init__(self):
                self._buffer = ""

            def write(inner_self, text):
                inner_self._buffer += text
                while "\n" in inner_self._buffer:
                    line, inner_self._buffer = inner_self._buffer.split("\n", 1)
                    if line.strip():
                        self.message.emit(line)

            def flush(inner_self):
                if inner_self._buffer.strip():
                    self.message.emit(inner_self._buffer)
                    inner_self._buffer = ""

        old_stdout = getattr(sys, "stdout", None)
        sys.stdout = StreamWrapper() if old_stdout is not None else old_stdout
        try:
            yield
        finally:
            if old_stdout is not None:
                sys.stdout.flush()
                sys.stdout = old_stdout


class Main(_Main):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parse_arguments()
        self.check_for_blast()

    def parse_arguments(self):
        parser = ArgumentParser()
        parser.add_argument("--reset", action="store_true", help="Reset the BLAST+ directory")
        args = parser.parse_args()

        if args.reset:
            dump_user_blast_path(None)

    def check_for_blast(self):
        while not check_binaries_in_path():
            msgBox = QtWidgets.QMessageBox(self.window())
            msgBox.setWindowModality(QtCore.Qt.WindowModal)
            msgBox.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
            msgBox.setWindowTitle(app.config.title)
            msgBox.setIcon(QtWidgets.QMessageBox.Question)
            msgBox.setText("BLAST+ was not found on your system. What would you like to do?" + " " * 15)
            msgBox.setInformativeText(
                "You can choose to automatically download the latest version of BLAST+, "
                "manually locate an existing BLAST+ installation on your computer, "
                "or skip this step and continue using the program with its other features."
            )

            msgBox.addButton("Download", QtWidgets.QMessageBox.AcceptRole)
            msgBox.addButton("Browse", QtWidgets.QMessageBox.ActionRole)
            msgBox.addButton("Skip", QtWidgets.QMessageBox.RejectRole)

            self.window().msgShow(msgBox)

            role = msgBox.buttonRole(msgBox.clickedButton())

            match role:
                case QtWidgets.QMessageBox.AcceptRole:
                    self.download_blast()
                case QtWidgets.QMessageBox.ActionRole:
                    self.browse_blast()
                case QtWidgets.QMessageBox.RejectRole:
                    break

    def download_blast(self):
        dlg = DownloaderDialog()
        dlg.exec()

    def browse_blast(self):
        dir = suggest_user_blast_path()
        dir.mkdir(parents=True, exist_ok=True)
        filename = QtWidgets.QFileDialog.getExistingDirectory(
            self.window(), f"{app.config.title} - Browse BLAST+", dir=str(dir)
        )
        if filename:
            path = Path(filename)
            dump_user_blast_path(path)

    def reject(self):
        if not app.model.items.tasks.children:
            return True
        return super().reject()
