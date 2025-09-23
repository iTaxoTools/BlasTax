from PySide6 import QtCore, QtWidgets

from argparse import ArgumentParser
from pathlib import Path

from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.main import Main as _Main

from .blast import check_binaries_in_path, dump_user_blast_path, suggest_user_blast_path


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
        raise NotImplementedError()

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
