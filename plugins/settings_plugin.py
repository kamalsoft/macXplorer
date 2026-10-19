"""Persistent explorer preferences and their settings dialog."""

import logging
from pathlib import Path
from typing import Sequence

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.theme import (
    ADVANCED_THEME_CATALOG,
    COLOR_TREATMENT_OPTIONS,
    CONTRAST_OPTIONS,
    DENSITY_OPTIONS,
    TEXT_SIZE_OPTIONS,
    THEME_COLORS,
    THEME_OPTIONS,
    system_theme_name,
    theme_stylesheet,
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
        self.setMinimumSize(760, 560)
        self.resize(900, 720)

        layout = QVBoxLayout(self)
        self.settings_tabs = QTabWidget(self)
        layout.addWidget(self.settings_tabs, 1)

        general_page = QWidget(self.settings_tabs)
        general_layout = QVBoxLayout(general_page)
        general_scroll = QScrollArea(general_page)
        general_scroll.setWidgetResizable(True)
        general_content = QWidget(general_scroll)
        form = QFormLayout(general_content)
        general_scroll.setWidget(general_content)
        general_layout.addWidget(general_scroll)
        self.settings_tabs.addTab(general_page, "General")

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

        themes_page = QWidget(self.settings_tabs)
        themes_layout = QVBoxLayout(themes_page)
        themes_scroll = QScrollArea(themes_page)
        themes_scroll.setWidgetResizable(True)
        themes_content = QWidget(themes_scroll)
        themes_content_layout = QVBoxLayout(themes_content)
        themes_form = QFormLayout()
        themes_content_layout.addLayout(themes_form)
        themes_scroll.setWidget(themes_content)
        themes_layout.addWidget(themes_scroll)
        self.settings_tabs.addTab(themes_page, "Themes")

        self.theme_selector = QComboBox(self)
        for label, theme_id in THEME_OPTIONS:
            self.theme_selector.addItem(label, theme_id)
        selected_theme = str(settings.value("appearance/theme", "system")).lower()
        theme_index = self.theme_selector.findData(selected_theme)
        self.theme_selector.setCurrentIndex(theme_index if theme_index >= 0 else 0)
        themes_form.addRow("Active appearance preset:", self.theme_selector)

        self.text_size_selector = self._add_choice(
            themes_form,
            "Text size:",
            TEXT_SIZE_OPTIONS,
            str(settings.value("appearance/textSize", "standard")),
        )
        self.density_selector = self._add_choice(
            themes_form,
            "Interface density:",
            DENSITY_OPTIONS,
            str(settings.value("appearance/density", "comfortable")),
        )
        self.contrast_selector = self._add_choice(
            themes_form,
            "Contrast:",
            CONTRAST_OPTIONS,
            str(settings.value("appearance/contrast", "standard")),
        )
        self.color_treatment_selector = self._add_choice(
            themes_form,
            "Color treatment:",
            COLOR_TREATMENT_OPTIONS,
            str(settings.value("appearance/colorTreatment", "standard")),
        )

        self.theme_preview = QWidget(self)
        self.theme_preview.setObjectName("themePreview")
        preview_layout = QVBoxLayout(self.theme_preview)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        preview_layout.addWidget(
            QLabel("Preview the selected appearance", self.theme_preview)
        )

        preview_content = QHBoxLayout()
        self.preview_file_list = QListWidget(self.theme_preview)
        self.preview_file_list.addItems(["Documents", "Pictures", "Downloads"])
        self.preview_file_list.setCurrentRow(1)
        preview_content.addWidget(self.preview_file_list, 1)

        preview_controls = QVBoxLayout()
        preview_controls.addWidget(QLabel("Sample file name", self.theme_preview))
        self.preview_input = QLineEdit("Quarterly report.pdf", self.theme_preview)
        preview_controls.addWidget(self.preview_input)
        preview_controls.addWidget(QLabel("Selected item preview", self.theme_preview))
        self.preview_button = QPushButton("Sample action", self.theme_preview)
        preview_controls.addWidget(self.preview_button)
        preview_controls.addStretch()
        preview_content.addLayout(preview_controls, 2)
        preview_layout.addLayout(preview_content)

        appearance_group = QGroupBox("Appearance preview", self)
        appearance_layout = QVBoxLayout(appearance_group)
        appearance_layout.addWidget(self.theme_preview)
        appearance_layout.addWidget(
            QLabel("This preview does not change the app until you save.", appearance_group)
        )
        themes_content_layout.addWidget(appearance_group)

        catalog_group = QGroupBox("Advanced UI theme catalog", themes_content)
        catalog_layout = QVBoxLayout(catalog_group)
        catalog_layout.addWidget(
            QLabel(
                "Browse design directions and their implementation status. "
                "Catalog entries are informational and do not change the active preset.",
                catalog_group,
            )
        )
        self.theme_search = QLineEdit(catalog_group)
        self.theme_search.setPlaceholderText("Search advanced themes…")
        self.theme_search.setClearButtonEnabled(True)
        catalog_layout.addWidget(self.theme_search)

        catalog_content = QHBoxLayout()
        self.advanced_theme_list = QListWidget(catalog_group)
        self.advanced_theme_list.setMinimumWidth(220)
        self.advanced_theme_list.setMaximumHeight(250)
        self.theme_details = QWidget(catalog_group)
        details_layout = QVBoxLayout(self.theme_details)
        details_layout.setContentsMargins(8, 4, 8, 4)
        self.theme_detail_name = QLabel(self.theme_details)
        self.theme_detail_name.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.theme_detail_category = QLabel(self.theme_details)
        self.theme_detail_status = QLabel(self.theme_details)
        self.theme_detail_status.setWordWrap(True)
        self.theme_detail_description = QLabel(self.theme_details)
        self.theme_detail_description.setWordWrap(True)
        self.theme_detail_note = QLabel(self.theme_details)
        self.theme_detail_note.setWordWrap(True)
        for detail in (
            self.theme_detail_name,
            self.theme_detail_category,
            self.theme_detail_status,
            self.theme_detail_description,
            self.theme_detail_note,
        ):
            details_layout.addWidget(detail)
        details_layout.addStretch()
        catalog_content.addWidget(self.advanced_theme_list, 1)
        catalog_content.addWidget(self.theme_details, 2)
        catalog_layout.addLayout(catalog_content)
        themes_content_layout.addWidget(catalog_group)
        themes_content_layout.addStretch()
        for theme_info in ADVANCED_THEME_CATALOG:
            self.advanced_theme_list.addItem(theme_info.name)
            self.advanced_theme_list.item(
                self.advanced_theme_list.count() - 1
            ).setData(Qt.ItemDataRole.UserRole, theme_info)
        self.theme_search.textChanged.connect(self._filter_advanced_themes)
        self.advanced_theme_list.currentItemChanged.connect(
            self._show_advanced_theme_details
        )
        self.advanced_theme_list.setCurrentRow(0)

        self.theme_selector.currentIndexChanged.connect(self._update_theme_preview)
        self.text_size_selector.currentIndexChanged.connect(self._update_theme_preview)
        self.density_selector.currentIndexChanged.connect(self._update_theme_preview)
        self.contrast_selector.currentIndexChanged.connect(self._update_theme_preview)
        self.color_treatment_selector.currentIndexChanged.connect(
            self._update_theme_preview
        )
        application = QApplication.instance()
        if application is not None:
            color_scheme_changed = getattr(
                application.styleHints(), "colorSchemeChanged", None
            )
            if color_scheme_changed is not None:
                color_scheme_changed.connect(self._on_system_color_scheme_changed)
        self._update_theme_preview()

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

    def _filter_advanced_themes(self, query: str) -> None:
        search_text = query.strip().casefold()
        first_visible_row = -1
        for row in range(self.advanced_theme_list.count()):
            item = self.advanced_theme_list.item(row)
            theme_info = item.data(Qt.ItemDataRole.UserRole)
            searchable = " ".join(
                (
                    theme_info.name,
                    theme_info.category,
                    theme_info.description,
                    theme_info.implementation_note,
                )
            ).casefold()
            item.setHidden(bool(search_text) and search_text not in searchable)
            if not item.isHidden() and first_visible_row < 0:
                first_visible_row = row
        if first_visible_row < 0:
            self.advanced_theme_list.setCurrentRow(-1)
            self._show_advanced_theme_details(None)
        elif (
            self.advanced_theme_list.currentRow() < 0
            or self.advanced_theme_list.currentItem().isHidden()
        ):
            self.advanced_theme_list.setCurrentRow(first_visible_row)

    def _show_advanced_theme_details(self, current, _previous=None) -> None:
        theme_info = (
            current.data(Qt.ItemDataRole.UserRole) if current is not None else None
        )
        if theme_info is None:
            self.theme_detail_name.clear()
            self.theme_detail_category.clear()
            self.theme_detail_status.clear()
            self.theme_detail_description.clear()
            self.theme_detail_note.clear()
            return
        self.theme_detail_name.setText(theme_info.name)
        self.theme_detail_category.setText(f"Category: {theme_info.category}")
        self.theme_detail_status.setText(
            "Informational only - this catalog entry is not an active preset."
        )
        self.theme_detail_description.setText(theme_info.description)
        self.theme_detail_note.setText(theme_info.implementation_note)

    def _bool_value(self, key: str, default: bool) -> bool:
        value = self.settings.value(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)

    def _add_choice(
        self,
        form: QFormLayout,
        label: str,
        options: tuple[tuple[str, str], ...],
        selected: str,
    ) -> QComboBox:
        selector = QComboBox(self)
        for option_label, option_value in options:
            selector.addItem(option_label, option_value)
        index = selector.findData(selected)
        selector.setCurrentIndex(index if index >= 0 else 0)
        form.addRow(label, selector)
        return selector

    def _update_theme_preview(self, _index: int = 0) -> None:
        theme = self.theme_selector.currentData()
        if theme == "system":
            application = QApplication.instance()
            theme = system_theme_name(application) if application is not None else "light"
        if theme not in THEME_COLORS:
            theme = "light"
        self.theme_preview.setStyleSheet(
            theme_stylesheet(
                str(theme),
                text_size=str(self.text_size_selector.currentData()),
                density=str(self.density_selector.currentData()),
                contrast=str(self.contrast_selector.currentData()),
                color_treatment=str(self.color_treatment_selector.currentData()),
            )
        )

    def _on_system_color_scheme_changed(self, *_args) -> None:
        if self.theme_selector.currentData() == "system":
            self._update_theme_preview()

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
            "appearance/theme": self.theme_selector.currentData(),
            "appearance/textSize": self.text_size_selector.currentData(),
            "appearance/density": self.density_selector.currentData(),
            "appearance/contrast": self.contrast_selector.currentData(),
            "appearance/colorTreatment": self.color_treatment_selector.currentData(),
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
