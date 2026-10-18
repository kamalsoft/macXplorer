"""Live text, image, and file metadata previews."""

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Sequence

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QPixmap
from PyQt6.QtWidgets import (
    QLabel,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from plugins.base import BasePlugin, PluginMetadata

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp"}
TEXT_SUFFIXES = {
    ".txt", ".py", ".js", ".json", ".html", ".css", ".md", ".csv",
    ".sh", ".log", ".plist", ".yaml", ".yml", ".xml", ".toml", ".ini",
}
MAX_PREVIEW_BYTES = 100 * 1024


class PreviewPlugin(BasePlugin):
    def __init__(self):
        self.core_app = None
        self.preview_pane: PreviewPane | None = None
        self._toolbar_actions: list[QAction] = []

    def initialize(self, core_app) -> None:
        self.core_app = core_app
        self.preview_pane = PreviewPane(core_app)
        core_app.splitter.addWidget(self.preview_pane)
        core_app.splitter.setStretchFactor(0, 1)
        core_app.splitter.setStretchFactor(1, 0)
        core_app.splitter.setSizes([850, 340])
        self.set_visible(core_app._setting_bool("view/showPreview", True))
        core_app.fileSelected.connect(self.update_preview)

    def register_toolbar_actions(self) -> Sequence[QAction]:
        return self._toolbar_actions

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            "preview", "Preview", "Preview file contents and metadata.", "View"
        )

    def update_preview(self, file_path: str) -> None:
        if self.preview_pane is not None:
            self.preview_pane.update_preview(file_path)

    def set_visible(self, visible: bool) -> None:
        if self.preview_pane is not None:
            self.preview_pane.setVisible(visible)


class PreviewPane(QWidget):
    """Stacked preview area with text, image, and metadata views."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        title = QLabel("<b>File Preview</b>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #4ec9b0; font-size: 14px;")
        layout.addWidget(title)

        self.stack = QStackedWidget(self)
        self.info_label = QLabel("Select a file to preview")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)

        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)

        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stack.addWidget(self.info_label)
        self.stack.addWidget(self.text_preview)
        self.stack.addWidget(self.image_preview)
        layout.addWidget(self.stack)

    def update_preview(self, file_path: str) -> None:
        path = Path(file_path)
        if not path.exists():
            self._show_info("Select a file to preview")
            return
        if path.is_dir():
            self._show_info(f"<b>Folder:</b><br>{escape(str(path))}")
            return

        try:
            stat = path.stat()
        except OSError as error:
            self._show_info(
                f"<b>Unable to inspect file:</b><br>{escape(str(error))}"
            )
            return

        if path.suffix.lower() in IMAGE_SUFFIXES:
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                self.image_preview.setPixmap(
                    pixmap.scaled(
                        QSize(300, 300),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
                self.stack.setCurrentWidget(self.image_preview)
                return

        if path.suffix.lower() in TEXT_SUFFIXES and stat.st_size <= MAX_PREVIEW_BYTES:
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError as error:
                self._show_info(f"<b>Unable to read file:</b><br>{escape(str(error))}")
                return
            self.text_preview.setPlainText(content)
            self.stack.setCurrentWidget(self.text_preview)
            return

        modified = datetime.fromtimestamp(stat.st_mtime)
        metadata = (
            f"<b>File:</b> {escape(path.name)}<br>"
            f"<b>Path:</b> {escape(str(path))}<br>"
            f"<b>Size:</b> {stat.st_size:,} bytes "
            f"({stat.st_size / (1024 * 1024):.2f} MB)<br>"
            f"<b>Type:</b> {path.suffix.upper() or 'Unknown'}<br>"
            f"<b>Modified:</b> {modified:%Y-%m-%d %H:%M:%S}<br>"
            f"<b>Permissions:</b> {stat.st_mode & 0o777:04o}"
        )
        self._show_info(metadata)

    def _show_info(self, text: str) -> None:
        self.info_label.setText(text)
        self.stack.setCurrentWidget(self.info_label)
