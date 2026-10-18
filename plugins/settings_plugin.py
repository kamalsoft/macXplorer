"""Persistent explorer preferences and their settings dialog."""

import logging
from pathlib import Path
from typing import Sequence

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from plugins.base import BasePlugin, PluginMetadata

LOGGER = logging.getLogger(__name__)


class SettingsPlugin(BasePlugin):
    def __init__(self):
        self.core_app = None
        self._toolbar_actions: list[QAction] = []
        self._settings_action: QAction | None = None

    def initialize(self, core_app) -> None:
        self.core_app = core_app
        self._settings_action = QAction("Explorer Settings…", core_app)
        self._settings_action.setToolTip("Configure explorer behavior")
        self._settings_action.triggered.connect(self.open_settings)

    def register_toolbar_actions(self) -> Sequence[QAction]:
        return self._toolbar_actions

    def register_menu_actions(self):
        return {"File": [self._settings_action]}

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            "settings",
            "Settings",
            "Configure persistent explorer preferences.",
            "File",
        )

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.core_app.settings, self.core_app)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.core_app.apply_settings()


class SettingsDialog(QDialog):
    """Settings editor; changes are persisted only when the user accepts."""

    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Explorer Settings")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        self.left_path_input, left_directory = self._directory_input(
            str(settings.value("workspace/leftDirectory", str(Path.home())))
        )
        self.right_path_input, right_directory = self._directory_input(
            str(
                settings.value(
                    "workspace/rightDirectory",
                    str(
                        (Path.home() / "Downloads")
                        if (Path.home() / "Downloads").is_dir()
                        else Path.home()
                    ),
                )
            )
        )
        form.addRow("Left pane startup folder:", left_directory)
        form.addRow("Right pane startup folder:", right_directory)

        favorite_values = settings.value("workspace/favorites", [])
        if isinstance(favorite_values, str):
            favorite_values = [favorite_values]
        self.favorites_list = QListWidget(self)
        self.favorites_list.addItems(
            [str(value) for value in favorite_values]
            if isinstance(favorite_values, (list, tuple))
            else []
        )
        favorite_controls = QHBoxLayout()
        add_favorite = QPushButton("Add Folder…")
        add_favorite.clicked.connect(self._add_favorite)
        remove_favorite = QPushButton("Remove Selected")
        remove_favorite.clicked.connect(self._remove_favorite)
        favorite_controls.addWidget(add_favorite)
        favorite_controls.addWidget(remove_favorite)
        favorite_controls.addStretch()
        form.addRow("Favorites:", self.favorites_list)
        form.addRow("", favorite_controls)

        self.show_hidden = QCheckBox("Show hidden files and folders")
        self.show_hidden.setChecked(self._bool_value("files/showHidden", False))
        form.addRow("Files:", self.show_hidden)

        self.confirm_delete = QCheckBox("Ask before deleting files or folders")
        self.confirm_delete.setChecked(self._bool_value("files/confirmDelete", True))
        form.addRow("Deletion:", self.confirm_delete)

        self.show_preview = QCheckBox("Show the file preview pane")
        self.show_preview.setChecked(self._bool_value("view/showPreview", True))
        form.addRow("Preview:", self.show_preview)

        self.dual_pane = QCheckBox("Start with both file panes visible")
        self.dual_pane.setChecked(self._bool_value("workspace/dualPane", True))
        form.addRow("Workspace:", self.dual_pane)

        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        self.validation_label.setStyleSheet("color: #f48771;")
        layout.addWidget(self.validation_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _bool_value(self, key: str, default: bool) -> bool:
        value = self.settings.value(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)

    def _directory_input(self, initial: str) -> tuple[QLineEdit, QWidget]:
        container = QWidget(self)
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        path_input = QLineEdit(initial, container)
        path_input.setClearButtonEnabled(True)
        browse = QPushButton("Browse…", container)
        browse.clicked.connect(lambda: self._browse_directory(path_input))
        row.addWidget(path_input, 1)
        row.addWidget(browse)
        return path_input, container

    def _browse_directory(self, path_input: QLineEdit) -> None:
        selected = QFileDialog.getExistingDirectory(
            self,
            "Choose startup folder",
            path_input.text() or str(Path.home()),
        )
        if selected:
            path_input.setText(selected)

    def _save_and_accept(self) -> None:
        left = Path(self.left_path_input.text()).expanduser()
        right = Path(self.right_path_input.text()).expanduser()
        invalid = [
            label
            for label, path in (
                ("Left pane", left),
                ("Right pane", right),
            )
            if not path.is_dir()
        ]
        if invalid:
            message = f"Choose an existing folder for: {', '.join(invalid)}."
            self.validation_label.setText(message)
            QMessageBox.warning(self, "Invalid startup folder", message)
            return

        self.validation_label.clear()
        values = {
            "workspace/leftDirectory": str(left.resolve()),
            "workspace/rightDirectory": str(right.resolve()),
            "files/showHidden": self.show_hidden.isChecked(),
            "files/confirmDelete": self.confirm_delete.isChecked(),
            "view/showPreview": self.show_preview.isChecked(),
            "workspace/dualPane": self.dual_pane.isChecked(),
            "workspace/favorites": [
                self.favorites_list.item(index).text()
                for index in range(self.favorites_list.count())
            ],
        }
        for key, value in values.items():
            self.settings.setValue(key, value)
        self.settings.sync()
        if self.settings.status() != QSettings.Status.NoError:
            LOGGER.error("Unable to persist explorer settings: %s", self.settings.status())
            message = "Explorer settings could not be saved."
            self.validation_label.setText(message)
            QMessageBox.critical(self, "Settings Error", message)
            return
        self.accept()

    def _add_favorite(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self, "Choose favorite folder", str(Path.home())
        )
        if selected and not any(
            self.favorites_list.item(index).text() == selected
            for index in range(self.favorites_list.count())
        ):
            self.favorites_list.addItem(selected)

    def _remove_favorite(self) -> None:
        row = self.favorites_list.currentRow()
        if row >= 0:
            self.favorites_list.takeItem(row)
