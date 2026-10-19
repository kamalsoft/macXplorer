"""Background file transfers used by the main window."""

import shutil
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from PyQt6.QtCore import QThread, pyqtSignal


class TransferCancelled(Exception):
    """Raised inside a file copy when cancellation is requested."""


@dataclass(frozen=True)
class TransferTask:
    source: Path
    destination: Path
    operation: str
    replace_existing: bool = False


@dataclass(frozen=True)
class TransferResult:
    completed: tuple[TransferTask, ...]
    cancelled: bool
    error: OSError | ValueError | None = None


class FileTransferThread(QThread):
    progress = pyqtSignal(object, int, int, str, int)

    def __init__(self, tasks: Sequence[TransferTask], parent=None) -> None:
        super().__init__(parent)
        self.tasks = tuple(tasks)
        self._cancel_requested = threading.Event()
        self._completed_count = 0
        self.result: TransferResult | None = None

    def cancel(self) -> None:
        self._cancel_requested.set()

    def run(self) -> None:
        completed: list[TransferTask] = []
        cancelled = False
        error: OSError | ValueError | None = None
        try:
            for task in self.tasks:
                self._check_cancelled()
                if task.replace_existing:
                    self._remove_path(task.destination)
                self.progress.emit(
                    self,
                    len(completed),
                    len(self.tasks),
                    str(task.source),
                    0,
                )
                if task.operation == "move":
                    shutil.move(str(task.source), str(task.destination))
                else:
                    self._copy_to_destination(task)
                completed.append(task)
                self._completed_count = len(completed)
                self.progress.emit(
                    self,
                    len(completed),
                    len(self.tasks),
                    str(task.source),
                    0,
                )
        except TransferCancelled:
            cancelled = True
        except (OSError, ValueError) as transfer_error:
            error = transfer_error

        self.result = TransferResult(tuple(completed), cancelled, error)

    def _copy_to_destination(self, task: TransferTask) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".macxplorer-copy-", dir=task.destination.parent
        ) as temporary_directory:
            staged_destination = Path(temporary_directory) / task.destination.name
            if task.source.is_dir() and not task.source.is_symlink():
                shutil.copytree(
                    task.source,
                    staged_destination,
                    copy_function=lambda source, destination: self._copy_file(
                        source, destination, follow_symlinks=True
                    ),
                )
            else:
                self._copy_file(
                    str(task.source),
                    str(staged_destination),
                    follow_symlinks=False,
                )
            self._check_cancelled()
            staged_destination.replace(task.destination)

    def _copy_file(
        self,
        source_name: str,
        destination_name: str,
        *,
        follow_symlinks: bool,
    ) -> str:
        source = Path(source_name)
        destination = Path(destination_name)
        if source.is_symlink() and not follow_symlinks:
            self._check_cancelled()
            shutil.copy2(source, destination, follow_symlinks=False)
            return destination_name

        copied = 0
        with (
            source.open("rb") as source_file,
            destination.open("xb") as destination_file,
        ):
            while chunk := source_file.read(1024 * 1024):
                self._check_cancelled()
                destination_file.write(chunk)
                copied += len(chunk)
                self.progress.emit(
                    self,
                    self._completed_count,
                    len(self.tasks),
                    str(source),
                    copied,
                )
        shutil.copystat(
            source,
            destination,
            follow_symlinks=follow_symlinks,
        )
        return destination_name

    @staticmethod
    def _remove_path(path: Path) -> None:
        if path.is_symlink() or not path.is_dir():
            path.unlink()
        else:
            shutil.rmtree(path)

    def _check_cancelled(self) -> None:
        if self._cancel_requested.is_set():
            raise TransferCancelled
