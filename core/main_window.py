from __future__ import annotations

import logging
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from pathlib import PurePosixPath

from PyQt6.QtCore import QMimeData, QSettings, QUrl, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QDesktopServices, QFont, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QInputDialog,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSplitter,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from core.plugin_manager import PluginManager
from core.theme import DARK_THEME
from core.widgets import FilePane, WorkspaceTab

LOGGER = logging.getLogger(__name__)


class MacXplorer(QMainWindow):
    """Application shell and shared services used by feature plugins."""

    fileSelected = pyqtSignal(str)

    def __init__(self, settings: QSettings | None = None) -> None:
        application = QApplication.instance()
        if application is not None:
            application.setApplicationName("macXplorer")
            application.setApplicationDisplayName("macXplorer")
            application.setOrganizationName("MacExplorer")
            application.setFont(QFont("Helvetica Neue"))
        super().__init__()
        self.setWindowTitle("macXplorer")
        self.resize(1280, 800)
        self.settings = settings if settings is not None else QSettings("MacExplorer", "MacExplorer")
        self.clipboard_paths: list[Path] = []
        self.clipboard_operation = "copy"
        self.clipboard_path: Path | None = None  # Compatibility for existing plugins.
        self.search_text = ""
        self._active_pane: FilePane | None = None
        self._build_ui()
        self._create_menus()
        self.plugin_manager = PluginManager(self, self.toolbar, self.menus)
        application = QApplication.instance()
        if application is not None:
            application.setStyleSheet(DARK_THEME)
        self._load_plugins()

    @property
    def current_workspace(self) -> WorkspaceTab:
        workspace = self.workspaces.currentWidget()
        if not isinstance(workspace, WorkspaceTab):
            raise RuntimeError("macXplorer has no active workspace.")
        return workspace

    @property
    def left_pane(self) -> FilePane:
        return self.current_workspace.left_pane

    @property
    def right_pane(self) -> FilePane:
        return self.current_workspace.right_pane

    @property
    def splitter(self):
        """Retain the existing plugin API for the main content splitter."""
        return self.content_splitter

    @property
    def right_pane_visible(self) -> bool:
        return self.current_workspace.right_pane_visible

    @property
    def dual_pane_active(self) -> bool:
        return self.right_pane_visible

    @dual_pane_active.setter
    def dual_pane_active(self, enabled: bool) -> None:
        self.right_pane_visible = enabled

    @right_pane_visible.setter
    def right_pane_visible(self, visible: bool) -> None:
        self.current_workspace.set_dual_pane(visible)

    def _build_ui(self) -> None:
        self.content = QWidget(self)
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal, self.content)
        self.workspaces = QTabWidget(self.content_splitter)
        self.workspaces.setTabsClosable(True)
        self.workspaces.setMovable(True)
        self.workspaces.tabCloseRequested.connect(self.close_tab)
        self.workspaces.currentChanged.connect(self._on_workspace_changed)
        self.workspaces.tabBarDoubleClicked.connect(self._on_tab_double_clicked)

        layout = QVBoxLayout(self.content)
        layout.setContentsMargins(0, 0, 0, 0)
        self.search_box = QLineEdit(self.content)
        self.search_box.setPlaceholderText("Filter files in open tabs…")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.setAccessibleName("Search files in open workspaces")
        self.search_box.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_box)
        layout.addWidget(self.content_splitter)
        self.setCentralWidget(self.content)
        self.toolbar = QToolBar("Plugins", self)
        self.addToolBar(self.toolbar)
        self.statusBar().showMessage("Ready")
        self.new_tab()

    def _create_menus(self) -> None:
        self.menus: dict[str, QMenu] = {}
        file_menu = self.menuBar().addMenu("&File")
        self.menus["File"] = file_menu
        self._add_action(file_menu, "New Tab", self.new_tab, "Ctrl+T")
        self._add_action(file_menu, "New Window", self.new_window, "Ctrl+N")
        file_menu.addSeparator()
        self._add_action(file_menu, "New Folder", self.create_new_folder, "Ctrl+Shift+N")
        self._add_action(file_menu, "New Empty File", self.create_new_file)
        self._add_action(
            file_menu,
            "Rename",
            self.rename_item,
            "F2",
        )
        self._add_action(file_menu, "Move to Trash", self.delete_item)
        file_menu.addSeparator()
        self._add_action(file_menu, "Close Tab", self.close_current_tab, "Ctrl+W")

        edit_menu = self.menuBar().addMenu("&Edit")
        self.menus["Edit"] = edit_menu
        self._add_action(edit_menu, "Copy", self.copy_item, QKeySequence.StandardKey.Copy)
        self._add_action(edit_menu, "Cut", self.cut_item, QKeySequence.StandardKey.Cut)
        self._add_action(edit_menu, "Paste", self.paste_item, QKeySequence.StandardKey.Paste)
        self._add_action(edit_menu, "Select All", self.select_all, "Ctrl+A")
        edit_menu.addSeparator()
        self._add_action(edit_menu, "Move to Trash", self.delete_item, "Ctrl+Backspace")

        view_menu = self.menuBar().addMenu("&View")
        self.menus["View"] = view_menu
        self._add_action(view_menu, "Back", self.navigate_back, "Ctrl+[")
        self._add_action(view_menu, "Forward", self.navigate_forward, "Ctrl+]")
        self._add_action(view_menu, "Up", self.navigate_up)
        self._add_action(view_menu, "Home", self.navigate_home)
        self._add_action(view_menu, "Focus Path", self.focus_path, "Ctrl+L")
        self._add_action(view_menu, "Search", self.focus_search, "Ctrl+F")
        view_menu.addSeparator()
        for label, mode in (("Details", "details"), ("List", "list"), ("Icons", "icons")):
            self._add_action(view_menu, label, lambda _checked=False, m=mode: self.set_view_mode(m))
        self._add_action(view_menu, "Toggle Dual Pane", self.toggle_dual_pane, "Ctrl+Shift+D")
        self._add_action(view_menu, "Browse Photos", self.browse_photos)
        self.image_filter_action = QAction("Show Images Only", self)
        self.image_filter_action.setCheckable(True)
        self.image_filter_action.toggled.connect(self._set_images_only)
        view_menu.addAction(self.image_filter_action)
        view_menu.aboutToShow.connect(self._sync_image_filter_action)

        tools_menu = self.menuBar().addMenu("&Tools")
        self.menus["Tools"] = tools_menu
        self._add_action(tools_menu, "Open in Finder", self.reveal_in_finder)
        self._add_action(tools_menu, "Open Selected Item", self.open_selected, "Ctrl+O")
        self._add_action(tools_menu, "Get Info", self.show_properties, "Ctrl+I")
        self._add_action(tools_menu, "Compress to ZIP", self.compress_selection)
        self._add_action(tools_menu, "Extract ZIP Here", self.extract_archive)

        self.go_menu = self.menuBar().addMenu("&Go")
        self._add_action(self.go_menu, "Add Current Folder to Favorites", self.add_favorite)
        self.favorites_menu = self.go_menu.addMenu("Favorites")
        self.locations_menu = self.go_menu.addMenu("Locations")
        self.recent_menu = self.go_menu.addMenu("Recent Files")
        self._refresh_go_menus()

    def _add_action(
        self,
        menu: QMenu,
        label: str,
        callback,
        shortcut: QKeySequence.StandardKey | str | None = None,
    ) -> QAction:
        action = QAction(label, self)
        if shortcut is not None:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(lambda _checked=False: callback())
        menu.addAction(action)
        return action

    def _load_plugins(self) -> None:
        self.plugin_manager.load_plugins()
        if self.plugin_manager.errors:
            details = "\n".join(self.plugin_manager.errors)
            LOGGER.error("One or more plugins could not be loaded:\n%s", details)
            QMessageBox.warning(
                self,
                "Plugin Loading Warning",
                "Some plugins could not be loaded. See the application log for details.\n\n"
                + details,
            )

    def _startup_path(self) -> Path:
        configured = self.settings.value(
            "workspace/leftDirectory", self.settings.value("workspace/startupPath", str(Path.home()))
        )
        path = Path(str(configured)).expanduser()
        return path if path.is_dir() else Path.home()

    def new_tab(self, path: str | Path | None = None) -> None:
        if path is not None:
            start_path = Path(path).expanduser()
        elif self.workspaces.count():
            start_path = Path(self.active_pane().path_bar.text())
        else:
            start_path = self._startup_path()
        if not start_path.is_dir():
            start_path = Path.home()
        right_path = Path(
            str(self.settings.value("workspace/rightDirectory", str(Path.home() / "Downloads")))
        ).expanduser()
        if not right_path.is_dir():
            right_path = Path.home()
        workspace = WorkspaceTab(
            str(start_path),
            str(right_path),
            show_hidden=self._setting_bool("files/showHidden", False),
            dual_pane=self._setting_bool("workspace/dualPane", True),
            parent=self,
        )
        for pane in (workspace.left_pane, workspace.right_pane):
            pane.filter_files(self.search_text)
            pane.directoryChanged.connect(
                lambda current_path, w=workspace: self._on_path_changed(w, current_path)
            )
            pane.currentPathChanged.connect(
                lambda selected_path, p=pane, w=workspace: self._on_pane_path_changed(
                    w, p, selected_path
                )
            )
            pane.fileActivated.connect(self._open_activated_path)
            pane.focused.connect(lambda p=pane: self._set_active_pane(p))
            pane.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            pane.customContextMenuRequested.connect(
                lambda position, p=pane: self._show_file_context_menu(p, position)
            )
        self.workspaces.addTab(workspace, start_path.name or str(start_path))
        self.workspaces.setCurrentWidget(workspace)
        self._set_active_pane(workspace.left_pane)
        workspace.left_pane.setFocus()

    def close_tab(self, index: int) -> None:
        if self.workspaces.count() == 1:
            self.new_tab()
        widget = self.workspaces.widget(index)
        if widget is not None:
            self.workspaces.removeTab(index)
            widget.deleteLater()

    def close_current_tab(self) -> None:
        self.close_tab(self.workspaces.currentIndex())

    def new_window(self) -> None:
        app_script = Path(__file__).resolve().parent.parent / "macXplorer.py"
        command = [sys.executable]
        if not getattr(sys, "frozen", False):
            command.append(str(app_script))
        try:
            subprocess.Popen(command, close_fds=True)
        except OSError as error:
            LOGGER.exception("Unable to open a new macXplorer window")
            QMessageBox.critical(self, "New Window", f"Could not open a new window: {error}")

    def _on_tab_double_clicked(self, index: int) -> None:
        if index < 0:
            self.new_tab()

    def _on_workspace_changed(self, _index: int) -> None:
        if self.workspaces.count():
            self._set_active_pane(self.current_workspace.active_pane)
            self.fileSelected.emit(str(self.active_pane().selected_path() or ""))

    def _on_path_changed(self, workspace: WorkspaceTab, path: str) -> None:
        if self.workspaces.currentWidget() is workspace:
            index = self.workspaces.currentIndex()
            self.workspaces.setTabText(index, Path(path).name or path)

    def _on_pane_path_changed(
        self, workspace: WorkspaceTab, pane: FilePane, path: str
    ) -> None:
        if self.workspaces.currentWidget() is workspace and self.active_pane() is pane:
            self._on_file_selected(path)

    def active_pane(self) -> FilePane:
        if self.workspaces.count() and self._active_pane in (
            self.left_pane,
            self.right_pane,
        ):
            return self._active_pane
        return self.left_pane

    def _set_active_pane(self, pane: FilePane) -> None:
        self._active_pane = pane
        self.current_workspace.active_pane = pane
        selected = pane.selected_path()
        self.fileSelected.emit(str(selected) if selected else "")

    def _on_file_selected(self, path: str) -> None:
        self.statusBar().showMessage(path)
        self.fileSelected.emit(path)

    def _open_activated_path(self, path: str) -> None:
        target = Path(path)
        if target.is_dir():
            return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(path)):
            QMessageBox.warning(self, "Open", f"macOS could not open:\n{path}")
            return
        self._remember_recent(target)

    def _remember_recent(self, path: Path) -> None:
        recent = [
            str(item)
            for item in self.settings.value("history/recentFiles", [])
            if Path(str(item)) != path
        ]
        recent.insert(0, str(path))
        self.settings.setValue("history/recentFiles", recent[:12])
        self.settings.sync()
        self._refresh_go_menus()

    def add_favorite(self) -> None:
        path = Path(self.active_pane().path_bar.text())
        favorites = self._setting_list("workspace/favorites")
        if str(path) not in favorites:
            favorites.append(str(path))
            self.settings.setValue("workspace/favorites", favorites)
            self.settings.sync()
            self._refresh_go_menus()

    def _refresh_go_menus(self) -> None:
        self.favorites_menu.clear()
        favorites = self._setting_list("workspace/favorites")
        for value in favorites:
            path = Path(str(value)).expanduser()
            if path.is_dir():
                self._add_action(
                    self.favorites_menu,
                    path.name or str(path),
                    lambda p=path: self.active_pane().navigate_to(str(p)),
                )
        if not self.favorites_menu.actions():
            action = self.favorites_menu.addAction("No favorites")
            action.setEnabled(False)

        self.locations_menu.clear()
        locations = [
            ("Home", Path.home()),
            ("Desktop", Path.home() / "Desktop"),
            ("Documents", Path.home() / "Documents"),
            ("Downloads", Path.home() / "Downloads"),
            ("Pictures", Path.home() / "Pictures"),
            ("Music", Path.home() / "Music"),
            ("Movies", Path.home() / "Movies"),
            ("Applications", Path("/Applications")),
            ("Computer", Path("/")),
        ]
        for label, path in locations:
            if path.is_dir():
                self._add_action(
                    self.locations_menu,
                    label,
                    lambda p=path: self.active_pane().navigate_to(str(p)),
                )
        volumes = Path("/Volumes")
        if volumes.is_dir():
            for volume in sorted(volumes.iterdir(), key=lambda item: item.name.casefold()):
                if volume.is_dir():
                    self._add_action(
                        self.locations_menu,
                        f"Volume: {volume.name}",
                        lambda p=volume: self.active_pane().navigate_to(str(p)),
                    )

        self.recent_menu.clear()
        recent = self._setting_list("history/recentFiles")
        for value in recent:
            path = Path(str(value)).expanduser()
            if path.is_file():
                self._add_action(
                    self.recent_menu,
                    path.name,
                    lambda p=path: self._open_activated_path(str(p)),
                )
        if not self.recent_menu.actions():
            action = self.recent_menu.addAction("No recent files")
            action.setEnabled(False)

    def _setting_list(self, key: str) -> list[str]:
        value = self.settings.value(key, [])
        if isinstance(value, str):
            return [value]
        if isinstance(value, (list, tuple)):
            return [str(item) for item in value]
        return []

    def on_search_changed(self, text: str) -> None:
        self.search_text = text
        for index in range(self.workspaces.count()):
            workspace = self.workspaces.widget(index)
            if isinstance(workspace, WorkspaceTab):
                workspace.left_pane.filter_files(text)
                workspace.right_pane.filter_files(text)

    def focus_path(self) -> None:
        self.active_pane().path_bar.setFocus()
        self.active_pane().path_bar.selectAll()

    def focus_search(self) -> None:
        search = getattr(self, "search_box", None)
        if search is not None:
            search.setFocus()
            search.selectAll()

    def navigate_back(self) -> None:
        self.active_pane().navigate_back()

    def navigate_forward(self) -> None:
        self.active_pane().navigate_forward()

    def navigate_up(self) -> None:
        self.active_pane().navigate_up()

    def navigate_home(self) -> None:
        self.active_pane().navigate_to(Path.home())

    def set_view_mode(self, mode: str) -> None:
        self.active_pane().set_view_mode(mode)

    def browse_photos(self) -> None:
        pictures = Path.home() / "Pictures"
        if not pictures.is_dir():
            selected = QFileDialog.getExistingDirectory(
                self, "Choose a photo folder", str(Path.home())
            )
            if not selected:
                return
            pictures = Path(selected)
        self.active_pane().navigate_to(str(pictures))
        self.active_pane().set_images_only(True)
        self.active_pane().set_view_mode("icons")
        self._sync_image_filter_action()

    def _set_images_only(self, enabled: bool) -> None:
        self.active_pane().set_images_only(enabled)
        if enabled:
            self.active_pane().set_view_mode("icons")

    def _sync_image_filter_action(self) -> None:
        enabled = self.active_pane().images_only
        self.image_filter_action.blockSignals(True)
        self.image_filter_action.setChecked(enabled)
        self.image_filter_action.blockSignals(False)

    def toggle_dual_pane(self) -> None:
        plugin = self.plugin_manager.get_plugin("workspace")
        enabled = not self.right_pane_visible
        if plugin is not None:
            plugin.set_dual_pane(enabled)
        else:
            self.current_workspace.set_dual_pane(enabled)

    def select_all(self) -> None:
        self.active_pane().view.selectAll()

    def _selected_paths(self) -> list[Path]:
        return self.active_pane().selected_paths()

    def _show_file_context_menu(self, pane: FilePane, position) -> None:
        index = pane.view.indexAt(position)
        if index.isValid():
            pane.view.setCurrentIndex(index)
        self._set_active_pane(pane)
        menu = QMenu(self)
        self._add_action(menu, "Open", self.open_selected)
        menu.addSeparator()
        self._add_action(menu, "Cut", self.cut_item, QKeySequence.StandardKey.Cut)
        self._add_action(menu, "Copy", self.copy_item, QKeySequence.StandardKey.Copy)
        self._add_action(menu, "Paste", self.paste_item, QKeySequence.StandardKey.Paste)
        self._add_action(menu, "Rename", self.rename_item)
        self._add_action(menu, "Move to Trash", self.delete_item)
        menu.addSeparator()
        self._add_action(menu, "Open in Finder", self.reveal_in_finder)
        self._add_action(menu, "Get Info", self.show_properties)
        menu.exec(pane.view.viewport().mapToGlobal(position))

    def open_selected(self) -> None:
        path = self.active_pane().selected_path()
        if path is None:
            return
        if path.is_dir():
            self.active_pane().navigate_to(path)
        else:
            self._open_activated_path(str(path))

    def create_new_folder(self) -> None:
        parent_dir = self.active_pane().selected_directory()
        folder_name, accepted = QInputDialog.getText(self, "New Folder", "Folder Name:")
        if not accepted or not folder_name.strip():
            return
        name = folder_name.strip()
        if name in {".", ".."} or Path(name).name != name:
            QMessageBox.warning(self, "Invalid Folder Name", "Enter a single folder name.")
            return
        try:
            (parent_dir / name).mkdir(exist_ok=False)
        except OSError as error:
            LOGGER.exception("Failed to create folder in %s", parent_dir)
            QMessageBox.critical(self, "Error", f"Failed to create folder: {error}")

    def create_new_file(self) -> None:
        parent_dir = self.active_pane().selected_directory()
        name, accepted = QInputDialog.getText(self, "New File", "File Name:")
        if not accepted or not name.strip():
            return
        if Path(name).name != name.strip() or name.strip() in {".", ".."}:
            QMessageBox.warning(self, "Invalid File Name", "Enter a single file name.")
            return
        try:
            (parent_dir / name.strip()).touch(exist_ok=False)
        except OSError as error:
            LOGGER.exception("Failed to create file in %s", parent_dir)
            QMessageBox.critical(self, "New File", f"Could not create the file: {error}")

    def rename_item(self) -> None:
        selected = self._selected_paths()
        if len(selected) != 1:
            QMessageBox.information(self, "Rename", "Select exactly one file or folder.")
            return
        source = selected[0]
        new_name, accepted = QInputDialog.getText(
            self, "Rename", "New name:", text=source.name
        )
        if not accepted or not new_name.strip() or new_name.strip() == source.name:
            return
        name = new_name.strip()
        if Path(name).name != name or name in {".", ".."}:
            QMessageBox.warning(self, "Rename", "Enter a valid single file or folder name.")
            return
        try:
            source.rename(source.with_name(name))
        except OSError as error:
            LOGGER.exception("Failed to rename %s", source)
            QMessageBox.critical(self, "Rename", f"Could not rename the item: {error}")

    def copy_item(self) -> None:
        self._set_clipboard("copy")

    def cut_item(self) -> None:
        self._set_clipboard("cut")

    def _set_clipboard(self, operation: str) -> None:
        paths = self._selected_paths()
        if not paths or any(not path.exists() and not path.is_symlink() for path in paths):
            QMessageBox.warning(self, "Clipboard", "Select one or more existing items.")
            return
        self.clipboard_paths = paths
        self.clipboard_path = paths[0]
        self.clipboard_operation = operation
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(path)) for path in paths])
        QApplication.clipboard().setMimeData(mime_data)
        self.statusBar().showMessage(f"{operation.title()} {len(paths)} item(s)")

    def paste_item(self) -> None:
        sources = list(self.clipboard_paths)
        if not sources:
            mime_data = QApplication.clipboard().mimeData()
            sources = [
                Path(url.toLocalFile())
                for url in (mime_data.urls() if mime_data is not None else [])
                if url.isLocalFile()
            ]
            self.clipboard_operation = "copy"
        sources = [
            path for path in sources if path.exists() or path.is_symlink()
        ]
        cut_sources = (
            list(self.clipboard_paths)
            if self.clipboard_operation == "cut"
            else []
        )
        remaining_cut: list[Path] = []
        if not sources:
            QMessageBox.warning(self, "Clipboard", "Nothing to paste.")
            return
        target_dir = self.active_pane().selected_directory()
        try:
            for source in sources:
                destination = target_dir / source.name
                if source.resolve() == target_dir.resolve() or (
                    source.is_dir()
                    and target_dir.resolve().is_relative_to(source.resolve())
                ):
                    raise ValueError("A folder cannot be copied into itself or its descendants.")
                if destination.exists() or destination.is_symlink():
                    answer = QMessageBox.warning(
                        self,
                        "Replace Existing Item?",
                        f"'{destination.name}' already exists. Replace it?",
                        QMessageBox.StandardButton.Yes
                        | QMessageBox.StandardButton.No
                        | QMessageBox.StandardButton.Cancel,
                        QMessageBox.StandardButton.Cancel,
                    )
                    if answer == QMessageBox.StandardButton.Cancel:
                        return
                    if answer == QMessageBox.StandardButton.No:
                        if self.clipboard_operation == "cut":
                            remaining_cut.append(source)
                        continue
                    self._remove_path(destination)
                if self.clipboard_operation == "cut":
                    shutil.move(str(source), str(destination))
                elif source.is_dir() and not source.is_symlink():
                    shutil.copytree(source, destination)
                else:
                    shutil.copy2(source, destination, follow_symlinks=False)
            if self.clipboard_operation == "cut":
                mime_data = QApplication.clipboard().mimeData()
                original_urls = [
                    url.toLocalFile()
                    for url in (mime_data.urls() if mime_data is not None else [])
                    if url.isLocalFile()
                ]
                if original_urls == [str(path) for path in cut_sources]:
                    if remaining_cut:
                        mime_data = QMimeData()
                        mime_data.setUrls(
                            [
                                QUrl.fromLocalFile(str(path))
                                for path in remaining_cut
                            ]
                        )
                        QApplication.clipboard().setMimeData(mime_data)
                    else:
                        QApplication.clipboard().clear()
                self.clipboard_paths = remaining_cut
                self.clipboard_path = remaining_cut[0] if remaining_cut else None
            self.statusBar().showMessage(f"Pasted to {target_dir}")
        except (OSError, ValueError) as error:
            LOGGER.exception("Failed to paste items into %s", target_dir)
            QMessageBox.critical(self, "Paste Error", f"Failed to paste: {error}")

    @staticmethod
    def _remove_path(path: Path) -> None:
        if path.is_symlink() or not path.is_dir():
            path.unlink()
        else:
            shutil.rmtree(path)

    def delete_item(self) -> None:
        self._delete_selected(permanent=False)

    def delete_immediately(self) -> None:
        self._delete_selected(permanent=True)

    def _delete_selected(self, permanent: bool) -> None:
        targets = self._selected_paths()
        targets = [path for path in targets if path.exists() or path.is_symlink()]
        if not targets:
            QMessageBox.warning(self, "Delete", "Select one or more items.")
            return
        operation = "Permanently delete" if permanent else "Move to Trash"
        if self._setting_bool("files/confirmDelete", True):
            answer = QMessageBox.question(
                self,
                operation,
                f"{operation} {len(targets)} selected item(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        try:
            for target in targets:
                if permanent:
                    self._remove_path(target)
                else:
                    self._move_to_trash(target)
            self.statusBar().showMessage(f"{operation}: {len(targets)} item(s)")
        except (OSError, subprocess.SubprocessError) as error:
            LOGGER.exception("Failed to %s selected items", operation.lower())
            QMessageBox.critical(self, "Delete Error", f"Could not {operation.lower()}: {error}")

    @staticmethod
    def _move_to_trash(path: Path) -> None:
        if sys.platform != "darwin":
            raise OSError("Moving items to Trash is supported only on macOS.")
        quoted_path = str(path.absolute()).replace("\\", "\\\\").replace('"', '\\"')
        script = f'tell application "Finder" to delete POSIX file "{quoted_path}"'
        subprocess.run(["/usr/bin/osascript", "-e", script], check=True, capture_output=True)

    def reveal_in_finder(self) -> None:
        path = self.active_pane().selected_path()
        if path is None:
            path = self.active_pane().current_path
        command = ["open", "-R", str(path)]
        try:
            subprocess.run(command, check=True, capture_output=True)
        except (OSError, subprocess.SubprocessError) as error:
            LOGGER.exception("Failed to reveal %s in Finder", path)
            QMessageBox.critical(self, "Finder", f"Could not reveal the item in Finder: {error}")

    def show_properties(self) -> None:
        path = self.active_pane().selected_path()
        if path is None:
            QMessageBox.information(self, "Get Info", "Select an item first.")
            return
        try:
            stat = path.lstat()
            kind = "Symbolic link" if path.is_symlink() else "Folder" if path.is_dir() else "File"
            details = (
                f"Name: {path.name}\n"
                f"Kind: {kind}\n"
                f"Location: {path.parent}\n"
                f"Size: {stat.st_size:,} bytes\n"
                f"Modified: {datetime.fromtimestamp(stat.st_mtime)}\n"
                f"Permissions: {stat.st_mode & 0o777:04o}"
            )
        except OSError as error:
            LOGGER.exception("Failed to read properties for %s", path)
            QMessageBox.critical(self, "Get Info", f"Could not read item properties: {error}")
            return
        QMessageBox.information(self, f"Info — {path.name}", details)

    def compress_selection(self) -> None:
        paths = self._selected_paths()
        if not paths:
            QMessageBox.information(self, "Compress", "Select one or more items to compress.")
            return
        target_dir = self.active_pane().selected_directory()
        archive_path, _ = QFileDialog.getSaveFileName(
            self, "Create ZIP Archive", str(target_dir / "Archive.zip"), "ZIP Archives (*.zip)"
        )
        if not archive_path:
            return
        output = Path(archive_path)
        if output.suffix.lower() != ".zip":
            output = output.with_suffix(".zip")
        try:
            self._create_zip(paths, target_dir, output)
        except (OSError, ValueError, zipfile.BadZipFile) as error:
            LOGGER.exception("Failed to create ZIP archive at %s", output)
            QMessageBox.critical(self, "Compress", f"Could not create the archive: {error}")

    @staticmethod
    def _create_zip(paths: list[Path], target_dir: Path, output: Path) -> None:
        output_resolved = output.resolve()
        for path in paths:
            if path.resolve() == output_resolved:
                raise ValueError("The output archive cannot be included in itself.")
            if (
                path.is_dir()
                and not path.is_symlink()
                and output_resolved.is_relative_to(path.resolve())
            ):
                raise ValueError("The output archive cannot be inside a folder being compressed.")
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in paths:
                if path.is_dir() and not path.is_symlink():
                    source_root = path.resolve()
                    if source_root != target_dir.resolve():
                        archive.write(path, path.relative_to(target_dir))
                    for child in path.rglob("*"):
                        if child.is_file() or child.is_symlink():
                            if child.resolve() != output_resolved:
                                archive.write(child, child.relative_to(target_dir))
                else:
                    archive.write(path, path.relative_to(target_dir))

    def extract_archive(self) -> None:
        path = self.active_pane().selected_path()
        if path is None or not path.is_file() or path.suffix.lower() != ".zip":
            QMessageBox.information(self, "Extract", "Select a ZIP archive first.")
            return
        destination = self.active_pane().current_path / path.stem
        try:
            self._extract_zip_to(path, destination)
        except (OSError, ValueError, zipfile.BadZipFile) as error:
            LOGGER.exception("Failed to extract %s", path)
            QMessageBox.critical(self, "Extract", f"Could not extract the archive: {error}")

    @staticmethod
    def _extract_zip_to(archive_path: Path, destination: Path) -> None:
        if destination.exists():
            raise FileExistsError(f"Destination already exists: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix=".macexplorer-extract-", dir=destination.parent
        ) as temporary:
            staging = Path(temporary)
            with zipfile.ZipFile(archive_path) as archive:
                for member in archive.infolist():
                    member_path = PurePosixPath(member.filename)
                    if member_path.is_absolute() or ".." in member_path.parts:
                        raise ValueError(f"Archive contains an unsafe path: {member.filename}")
                    resolved = (staging / Path(*member_path.parts)).resolve()
                    if not resolved.is_relative_to(staging.resolve()):
                        raise ValueError(f"Archive contains an unsafe path: {member.filename}")
                archive.extractall(staging)
            staging.rename(destination)

    def _setting_bool(self, key: str, default: bool) -> bool:
        value = self.settings.value(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"true", "1", "yes", "on"}

    def apply_settings(self) -> None:
        left = Path(str(self.settings.value("workspace/leftDirectory", str(Path.home())))).expanduser()
        right_default = Path.home() / "Downloads"
        if not right_default.is_dir():
            right_default = Path.home()
        right = Path(
            str(self.settings.value("workspace/rightDirectory", str(right_default)))
        ).expanduser()
        if not left.is_dir() or not right.is_dir():
            QMessageBox.warning(
                self,
                "Explorer Settings",
                "The configured startup folder no longer exists. Update it in Settings.",
            )
            return
        dual_pane = self._setting_bool("workspace/dualPane", True)
        show_hidden = self._setting_bool("files/showHidden", False)
        for index in range(self.workspaces.count()):
            workspace = self.workspaces.widget(index)
            if not isinstance(workspace, WorkspaceTab):
                continue
            workspace.left_pane.set_show_hidden(show_hidden)
            workspace.right_pane.set_show_hidden(show_hidden)
            workspace.set_dual_pane(dual_pane)
        self.left_pane.navigate_to(str(left))
        self.right_pane.navigate_to(str(right))
        preview = self.plugin_manager.get_plugin("preview")
        if preview is not None:
            preview.set_visible(self._setting_bool("view/showPreview", True))
        self._refresh_go_menus()
