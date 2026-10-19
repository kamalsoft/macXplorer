"""Product identity and About presentation for macXplorer."""

from pathlib import Path
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


def app_asset_path(name: str) -> Path:
    """Resolve app assets in source runs and PyInstaller bundles."""
    candidates: list[Path] = []
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root is not None:
        root = Path(bundle_root)
        candidates.extend((root / "assets" / name, root / "Resources" / "assets" / name))

    executable = Path(sys.executable).resolve()
    if executable.parent.name == "MacOS":
        candidates.append(
            executable.parent.parent / "Resources" / "assets" / name
        )
    candidates.append(Path(__file__).resolve().parent.parent / "assets" / name)

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Required macXplorer asset is missing: {name}")


def app_icon() -> QIcon:
    """Return the product icon used by the app and its windows."""
    return QIcon(str(app_asset_path("macXplorer.png")))


class AboutDialog(QDialog):
    """Compact product identity panel with honest development status."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("About macXplorer")
        self.setWindowIcon(app_icon())
        self.setFixedWidth(460)

        layout = QVBoxLayout(self)
        brand_row = QHBoxLayout()
        icon_label = QLabel(self)
        icon_label.setPixmap(
            QPixmap(str(app_asset_path("macXplorer.png"))).scaled(
                76,
                76,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        icon_label.setAccessibleName("macXplorer app icon")
        brand_row.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignTop)

        brand_text = QVBoxLayout()
        title = QLabel("macXplorer", self)
        title.setObjectName("brandTitle")
        tagline = QLabel("A considered workspace for your files.", self)
        tagline.setObjectName("brandTagline")
        brand_text.addWidget(title)
        brand_text.addWidget(tagline)
        brand_text.addStretch()
        brand_row.addLayout(brand_text, 1)
        layout.addLayout(brand_row)

        status = QLabel("DEVELOPMENT BUILD", self)
        status.setObjectName("brandStatus")
        status.setAccessibleDescription(
            "This application is under active development."
        )
        layout.addWidget(status, 0, Qt.AlignmentFlag.AlignLeft)

        description = QLabel(
            "A macOS file manager with tabbed workspaces, dual-pane browsing, "
            "previews, comparisons, and everyday file operations.",
            self,
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        attribution = QLabel("A NanovionLabs application", self)
        attribution.setObjectName("brandAttribution")
        layout.addWidget(attribution)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
