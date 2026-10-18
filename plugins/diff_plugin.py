"""Folder and text-file comparison plugin."""

import difflib
import filecmp
from html import escape
from pathlib import Path
from typing import Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from plugins.base import BasePlugin, PluginMetadata


class DiffPlugin(BasePlugin):
    def __init__(self):
        self.core_app = None
        self._toolbar_actions: list[QAction] = []

    def initialize(self, core_app) -> None:
        self.core_app = core_app
        style = core_app.style()
        folder_action = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon),
            "Compare Folders",
            core_app,
        )
        folder_action.setToolTip("Compare the current directories in both panes")
        folder_action.triggered.connect(self.compare_directories)

        file_action = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_FileIcon),
            "Compare Files",
            core_app,
        )
        file_action.setToolTip("Compare selected files from the left and right panes")
        file_action.triggered.connect(self.compare_files)
        self._toolbar_actions = [folder_action, file_action]

    def register_toolbar_actions(self) -> Sequence[QAction]:
        return self._toolbar_actions

    def register_menu_actions(self):
        return {"Tools": self._toolbar_actions}

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            "diff", "Diff", "Compare folders and files.", "Tools"
        )

    def compare_directories(self) -> None:
        core = self.core_app
        dialog = FolderCompareDialog(
            core.left_pane.path_bar.text(),
            core.right_pane.path_bar.text(),
            core,
        )
        dialog.exec()

    def compare_files(self) -> None:
        core = self.core_app
        left_file = core.left_pane.selected_path()
        right_file = core.right_pane.selected_path()
        if (
            left_file is None
            or right_file is None
            or not left_file.is_file()
            or not right_file.is_file()
        ):
            QMessageBox.warning(
                core,
                "Diff Error",
                "Select a valid file in both the left and right panes to compare.",
            )
            return
        FileDiffDialog(str(left_file), str(right_file), core).exec()


class FolderCompareDialog(QDialog):
    """Recursive directory comparison results."""

    def __init__(self, left_dir: str, right_dir: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Folder Comparison")
        self.resize(850, 500)
        self.left_dir = Path(left_dir)
        self.right_dir = Path(right_dir)

        layout = QVBoxLayout(self)
        label = QLabel(
            f"<b>Comparing:</b><br>Left: {escape(str(self.left_dir))}"
            f"<br>Right: {escape(str(self.right_dir))}"
        )
        label.setStyleSheet("color: #9cdcfe; margin-bottom: 8px;")
        layout.addWidget(label)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Path", "Status", "Details"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        self._run_comparison()
        buttons = QHBoxLayout()
        buttons.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    def _run_comparison(self) -> None:
        if not self.left_dir.is_dir() or not self.right_dir.is_dir():
            QMessageBox.warning(
                self, "Folder Comparison", "One or both directories do not exist."
            )
            return

        rows: list[tuple[str, str, str]] = []
        try:
            self._collect_comparison(self.left_dir, self.right_dir, Path(), rows)
        except OSError as error:
            QMessageBox.warning(
                self,
                "Folder Comparison",
                f"Unable to compare these folders: {error}",
            )
            return
        self.table.setRowCount(len(rows))
        colors = {
            "Unique to Left": Qt.GlobalColor.cyan,
            "Unique to Right": Qt.GlobalColor.magenta,
            "Different": Qt.GlobalColor.yellow,
            "Identical": Qt.GlobalColor.green,
        }
        for row_index, row in enumerate(rows):
            for column, text in enumerate(row):
                item = QTableWidgetItem(text)
                if column == 1:
                    item.setForeground(colors.get(text, Qt.GlobalColor.white))
                self.table.setItem(row_index, column, item)

    def _collect_comparison(
        self,
        left: Path,
        right: Path,
        relative: Path,
        rows: list[tuple[str, str, str]],
    ) -> None:
        comparison = filecmp.dircmp(left, right, ignore=[".DS_Store"])
        for name in sorted(comparison.left_only):
            rows.append((str(relative / name), "Unique to Left", str(left / name)))
        for name in sorted(comparison.right_only):
            rows.append((str(relative / name), "Unique to Right", str(right / name)))
        for name in sorted(comparison.diff_files):
            rows.append((str(relative / name), "Different", "File contents differ"))
        for name in sorted(comparison.same_files):
            rows.append((str(relative / name), "Identical", "Files match"))

        for name in sorted(comparison.common_dirs):
            self._collect_comparison(
                left / name, right / name, relative / name, rows
            )


class FileDiffDialog(QDialog):
    """Unified text-file diff dialog."""

    def __init__(self, file1: str, file2: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Diff Viewer")
        self.resize(900, 600)
        layout = QVBoxLayout(self)
        info = QLabel(
            f"<b>Diffing:</b> {escape(Path(file1).name)} "
            f"vs {escape(Path(file2).name)}"
        )
        info.setStyleSheet("color: #ce9178; margin-bottom: 4px;")
        layout.addWidget(info)

        self.diff_text = QTextEdit()
        self.diff_text.setReadOnly(True)
        layout.addWidget(self.diff_text)
        self._generate_diff(file1, file2)

        buttons = QHBoxLayout()
        buttons.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    def _generate_diff(self, file1: str, file2: str) -> None:
        try:
            with open(file1, encoding="utf-8", errors="replace") as left:
                left_lines = left.readlines()
            with open(file2, encoding="utf-8", errors="replace") as right:
                right_lines = right.readlines()
        except OSError as error:
            self.diff_text.setPlainText(f"Could not read files: {error}")
            return

        output = "\n".join(
            difflib.unified_diff(
                left_lines,
                right_lines,
                fromfile=file1,
                tofile=file2,
                lineterm="",
            )
        )
        self.diff_text.setPlainText(output or "Files are identical.")
