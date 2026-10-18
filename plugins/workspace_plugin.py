"""Dual-pane workspace controls and navigation shortcuts."""

from typing import Sequence

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QStyle

from plugins.base import BasePlugin, PluginMetadata


class WorkspacePlugin(BasePlugin):
    def __init__(self):
        self.core_app = None
        self._toolbar_actions: list[QAction] = []

    def initialize(self, core_app) -> None:
        self.core_app = core_app
        style = core_app.style()

        toggle = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView),
            "Toggle Dual Pane",
            core_app,
        )
        toggle.setCheckable(True)
        toggle.setChecked(core_app.dual_pane_active)
        toggle.setShortcut(QKeySequence("Ctrl+D"))
        toggle.setToolTip("Show or hide the right file pane")
        toggle.toggled.connect(self.set_dual_pane)

        parent = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_ArrowUp),
            "Parent Directory",
            core_app,
        )
        parent.setShortcut(QKeySequence("Ctrl+Up"))
        parent.triggered.connect(lambda: core_app.active_pane().go_to_parent())

        home = QAction(
            style.standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon),
            "Home Directory",
            core_app,
        )
        home.setShortcut(QKeySequence("Ctrl+Shift+H"))
        home.triggered.connect(lambda: core_app.active_pane().go_to_home())

        self._toolbar_actions = [toggle, parent, home]
        core_app.workspaces.currentChanged.connect(self._sync_dual_pane_action)
        self._sync_dual_pane_action()

    def register_toolbar_actions(self) -> Sequence[QAction]:
        return self._toolbar_actions

    def register_menu_actions(self):
        return {"View": self._toolbar_actions}

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            "workspace",
            "Workspace",
            "Manage panes and navigation.",
            "View",
        )

    def toggle_dual_pane(self) -> None:
        self.set_dual_pane(not self.core_app.right_pane_visible)

    def set_dual_pane(self, enabled: bool) -> None:
        core = self.core_app
        core.current_workspace.set_dual_pane(enabled)
        if self._toolbar_actions:
            toggle_action = self._toolbar_actions[0]
            toggle_action.blockSignals(True)
            toggle_action.setChecked(enabled)
            toggle_action.blockSignals(False)

    def _sync_dual_pane_action(self, _index: int = 0) -> None:
        if not self._toolbar_actions:
            return
        toggle_action = self._toolbar_actions[0]
        toggle_action.blockSignals(True)
        toggle_action.setChecked(self.core_app.right_pane_visible)
        toggle_action.blockSignals(False)
