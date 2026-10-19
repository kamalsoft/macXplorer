"""Reusable file-system widgets used by the core and plugins."""

from pathlib import Path

from PyQt6.QtCore import QDir, QModelIndex, QSize, QSortFilterProxyModel, Qt, pyqtSignal
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QLineEdit,
    QLabel,
    QListView,
    QStackedWidget,
    QSplitter,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

IMAGE_PATTERNS = [
    "*.bmp",
    "*.gif",
    "*.heic",
    "*.heif",
    "*.jpeg",
    "*.jpg",
    "*.png",
    "*.tif",
    "*.tiff",
    "*.webp",
]


class FocusLineEdit(QLineEdit):
    focused = pyqtSignal()

    def focusInEvent(self, event) -> None:
        self.focused.emit()
        super().focusInEvent(event)


class FocusTreeView(QTreeView):
    focused = pyqtSignal()

    def focusInEvent(self, event) -> None:
        self.focused.emit()
        super().focusInEvent(event)


class FocusListView(QListView):
    focused = pyqtSignal()

    def focusInEvent(self, event) -> None:
        self.focused.emit()
        super().focusInEvent(event)


class FilePane(QWidget):
    """A filesystem tree with directory navigation and native drag-and-drop."""

    focused = pyqtSignal()
    currentPathChanged = pyqtSignal(str)
    directoryChanged = pyqtSignal(str)
    fileActivated = pyqtSignal(str)

    def __init__(
        self,
        title: str,
        start_path: str,
        show_hidden: bool = False,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.title_label = QLabel(f"<b>{title}</b>")
        self.title_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.title_label)

        self.navigation_history: list[str] = []
        self.history_index = -1
        self._navigating_history = False

        navigation = QWidget(self)
        navigation_layout = QVBoxLayout(navigation)
        navigation_layout.setContentsMargins(0, 0, 0, 0)
        self.path_bar = FocusLineEdit(navigation)
        self.path_bar.setClearButtonEnabled(True)
        self.path_bar.setAccessibleName(f"{title} current directory")
        self.path_bar.setPlaceholderText("Go to folder path…")
        self.path_bar.returnPressed.connect(
            lambda: self.navigate_to(self.path_bar.text())
        )
        navigation_layout.addWidget(self.path_bar)
        layout.addWidget(navigation)

        self.source_model = QFileSystemModel(self)
        self.source_model.setRootPath(QDir.rootPath())
        self.source_model.setReadOnly(False)
        self.set_show_hidden(show_hidden)

        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.source_model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.images_only = False

        self.tree = FocusTreeView(self)
        self.tree.setModel(self.proxy_model)
        self.tree.setRootIsDecorated(False)
        self.tree.setItemsExpandable(False)
        self.tree.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.tree.setDragDropOverwriteMode(False)
        self.tree.setSortingEnabled(True)
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 70)
        self.tree.setColumnWidth(2, 90)
        self.list_view = FocusListView(self)
        self.list_view.setModel(self.proxy_model)
        self.list_view.setViewMode(QListView.ViewMode.ListMode)
        self.list_view.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.list_view.setDragEnabled(True)
        self.list_view.setAcceptDrops(True)
        self.list_view.setDropIndicatorShown(True)
        self.list_view.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)

        self.views = QStackedWidget(self)
        self.views.addWidget(self.tree)
        self.views.addWidget(self.list_view)
        layout.addWidget(self.views)

        self.tree.focused.connect(self.focused)
        self.path_bar.focused.connect(self.focused)
        self.list_view.focused.connect(self.focused)
        self.tree.clicked.connect(self._handle_click)
        self.tree.activated.connect(self._handle_activation)
        self.tree.selectionModel().currentChanged.connect(self._handle_current_changed)
        self.list_view.activated.connect(self._handle_activation)
        self.list_view.selectionModel().currentChanged.connect(self._handle_current_changed)

        target = Path(start_path)
        self.navigate_to(str(target if target.is_dir() else Path.home()))

    def navigate_to(self, path_str: str, *, record_history: bool = True) -> bool:
        target_path = Path(path_str).expanduser()
        if not target_path.is_dir():
            return False

        source_index = self.source_model.index(str(target_path))
        proxy_index = self.proxy_model.mapFromSource(source_index)
        if not source_index.isValid() or not proxy_index.isValid():
            return False

        self.tree.setRootIndex(proxy_index)
        self.list_view.setRootIndex(proxy_index)
        self.path_bar.setText(str(target_path))
        if record_history and not self._navigating_history:
            target = str(target_path.resolve())
            if self.history_index < 0 or self.navigation_history[self.history_index] != target:
                del self.navigation_history[self.history_index + 1:]
                self.navigation_history.append(target)
                self.history_index = len(self.navigation_history) - 1
        self.currentPathChanged.emit(str(target_path))
        self.directoryChanged.emit(str(target_path))
        return True

    def go_to_parent(self) -> None:
        self.navigate_to(str(Path(self.path_bar.text()).parent))

    def go_to_home(self) -> None:
        self.navigate_to(str(Path.home()))

    def go_back(self) -> None:
        if self.history_index > 0:
            self.history_index -= 1
            self._navigate_history_item()

    def navigate_back(self) -> None:
        self.go_back()

    def go_forward(self) -> None:
        if self.history_index + 1 < len(self.navigation_history):
            self.history_index += 1
            self._navigate_history_item()

    def navigate_forward(self) -> None:
        self.go_forward()

    def navigate_up(self) -> None:
        self.go_to_parent()

    def _navigate_history_item(self) -> None:
        self._navigating_history = True
        try:
            self.navigate_to(
                self.navigation_history[self.history_index], record_history=False
            )
        finally:
            self._navigating_history = False

    def filter_files(self, text: str) -> None:
        self.proxy_model.setFilterFixedString(text)

    def set_images_only(self, enabled: bool) -> None:
        self.images_only = enabled
        self.source_model.setNameFilters(IMAGE_PATTERNS if enabled else [])
        self.source_model.setNameFilterDisables(False)

    def set_view_mode(self, mode: str) -> None:
        if mode == "icons":
            self.list_view.setViewMode(QListView.ViewMode.IconMode)
            self.list_view.setResizeMode(QListView.ResizeMode.Adjust)
            self.list_view.setGridSize(QSize(112, 112))
            self.list_view.setIconSize(QSize(64, 64))
            self.views.setCurrentWidget(self.list_view)
        elif mode == "list":
            self.list_view.setViewMode(QListView.ViewMode.ListMode)
            self.views.setCurrentWidget(self.list_view)
        else:
            self.views.setCurrentWidget(self.tree)

    def sort_by(self, column: int, order: Qt.SortOrder) -> None:
        self.tree.sortByColumn(column, order)
        self.proxy_model.sort(column, order)

    def set_show_hidden(self, show_hidden: bool) -> None:
        filters = (
            QDir.Filter.AllEntries
            | QDir.Filter.NoDotAndDotDot
            | QDir.Filter.AllDirs
        )
        if show_hidden:
            filters |= QDir.Filter.Hidden
        self.source_model.setFilter(filters)

    def current_file_path(self) -> str:
        view = self.views.currentWidget()
        proxy_index = view.currentIndex()
        if proxy_index.isValid():
            source_index = self.proxy_model.mapToSource(proxy_index)
            if source_index.isValid():
                return self.source_model.filePath(source_index)
        return self.path_bar.text()

    def selected_path(self) -> Path | None:
        view = self.views.currentWidget()
        proxy_index = view.currentIndex()
        if not proxy_index.isValid():
            return None
        source_index = self.proxy_model.mapToSource(proxy_index)
        if not source_index.isValid():
            return None
        return Path(self.source_model.filePath(source_index))

    def selected_paths(self) -> list[Path]:
        view = self.views.currentWidget()
        return [
            Path(self.source_model.filePath(self.proxy_model.mapToSource(index)))
            for index in view.selectionModel().selectedRows(0)
            if self.proxy_model.mapToSource(index).isValid()
        ]

    @property
    def view(self):
        return self.views.currentWidget()

    @property
    def current_path(self) -> Path:
        return Path(self.path_bar.text())

    def selected_directory(self) -> Path:
        selected_path = Path(self.current_file_path())
        if selected_path.is_dir():
            return selected_path
        return selected_path.parent

    def _path_from_index(self, proxy_index: QModelIndex) -> str:
        source_index = self.proxy_model.mapToSource(proxy_index)
        return self.source_model.filePath(source_index)

    def _handle_click(self, proxy_index: QModelIndex) -> None:
        path = Path(self._path_from_index(proxy_index))
        if path.is_dir():
            self.path_bar.setText(str(path))

    def _handle_activation(self, proxy_index: QModelIndex) -> None:
        path = Path(self._path_from_index(proxy_index))
        if path.is_dir():
            self.navigate_to(str(path))
        else:
            self.fileActivated.emit(str(path))

    def _handle_current_changed(
        self, current: QModelIndex, _previous: QModelIndex
    ) -> None:
        if current.isValid():
            self.currentPathChanged.emit(self._path_from_index(current))


class WorkspaceTab(QWidget):
    """A tab containing the app's paired filesystem panes."""

    def __init__(
        self,
        left_path: str,
        right_path: str,
        show_hidden: bool = False,
        dual_pane: bool = True,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.active_pane = None
        self.right_pane_visible = dual_pane
        self.left_pane = FilePane(
            "Left", left_path, show_hidden=show_hidden, parent=self
        )
        self.right_pane = FilePane(
            "Right", right_path, show_hidden=show_hidden, parent=self
        )
        self.splitter.addWidget(self.left_pane)
        self.splitter.addWidget(self.right_pane)
        layout.addWidget(self.splitter)
        self.active_pane = self.left_pane
        self.left_pane.focused.connect(lambda: self._set_active_pane(self.left_pane))
        self.right_pane.focused.connect(lambda: self._set_active_pane(self.right_pane))
        self.set_dual_pane(dual_pane)

    def _set_active_pane(self, pane: FilePane) -> None:
        self.active_pane = pane

    def set_dual_pane(self, enabled: bool) -> None:
        self.right_pane_visible = enabled
        self.right_pane.setVisible(enabled)
        self.splitter.setSizes([500, 500] if enabled else [1000, 0])
