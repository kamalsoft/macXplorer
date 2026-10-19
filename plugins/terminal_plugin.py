"""Open macOS Terminal in the active file pane's directory."""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMessageBox

from plugins.base import BasePlugin, PluginMetadata

LOGGER = logging.getLogger(__name__)

TERMINAL_SCRIPT = """on run argv
    set targetPath to item 1 of argv
    tell application "Terminal"
        activate
        do script "cd " & quoted form of targetPath
    end tell
end run"""


class TerminalPlugin(BasePlugin):
    def __init__(self) -> None:
        self.core_app = None
        self._toolbar_actions: list[QAction] = []
        self._menu_actions: list[QAction] = []

    def initialize(self, core_app) -> None:
        self.core_app = core_app
        action = QAction("Open Terminal Here", core_app)
        action.setToolTip("Open macOS Terminal in the active folder")
        action.triggered.connect(self.open_terminal_here)
        self._menu_actions = [action]

    def register_toolbar_actions(self) -> Sequence[QAction]:
        return self._toolbar_actions

    def register_menu_actions(self) -> dict[str, Sequence[QAction]]:
        return {"Tools": self._menu_actions}

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            "terminal",
            "Terminal",
            "Open macOS Terminal in the active folder.",
            "Tools",
        )

    def open_terminal_here(self) -> None:
        core = self.core_app
        if sys.platform != "darwin":
            QMessageBox.warning(
                core,
                "Open Terminal Here",
                "This action is available only on macOS.",
            )
            return

        path = Path(core.active_pane().path_bar.text()).expanduser()
        if not path.is_dir():
            QMessageBox.warning(
                core,
                "Open Terminal Here",
                f"The active folder is no longer available:\n{path}",
            )
            return

        try:
            subprocess.run(
                [
                    "/usr/bin/osascript",
                    "-e",
                    TERMINAL_SCRIPT,
                    str(path.resolve()),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            LOGGER.exception("Could not open Terminal at %s", path)
            details = (
                error.stderr.strip()
                if isinstance(error, subprocess.CalledProcessError)
                and error.stderr
                else str(error)
            )
            QMessageBox.critical(
                core,
                "Open Terminal Here",
                f"Could not open Terminal in:\n{path}\n\n{details}",
            )
