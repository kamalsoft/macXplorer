# Architecture and Technical Reference

## System context

macXplorer is a desktop application implemented in Python with PyQt6. It uses Qt widgets and models for its user interface and local file-system browsing. macOS-specific integration includes the process display name and Finder operations such as moving items to Trash and revealing files.

```text
macXplorer.py
  QApplication and macOS process identity
  MacXplorer (core/main_window.py; main-window class)
    PluginManager
    QTabWidget
      WorkspaceTab (one per tab)
        FilePane: QFileSystemModel + proxy + tree/list views
        FilePane: QFileSystemModel + proxy + tree/list views
    Preview panel
    Shared menus, toolbar, settings, clipboard, and file operations
  plugins/
    DiffPlugin
    PreviewPlugin
    SettingsPlugin
    WorkspacePlugin
```

The core owns application-level state and common operations. Plugins contribute focused UI or behavior through the plugin contract. File panes and workspace tabs are reusable widgets in `core/widgets.py`.

## Runtime lifecycle

1. `macXplorer.py` sets the native macOS process name when running on macOS, creates `QApplication`, and sets application identity.
2. `MacXplorer` builds its menus, plugin toolbar, search field, and initial workspace. The user-facing application name is `macXplorer`.
3. `PluginManager` discovers Python modules under `plugins/`, also including the built-in module list for frozen builds.
4. Each plugin class is instantiated, checked for metadata, initialized with the core application, and asked for toolbar and menu actions.
5. The core enters the Qt event loop.

Plugin import, initialization, or registration failures are logged and collected by the manager. Startup displays a warning if plugin loading produced errors.

## Main components

| Component | Responsibility |
| --- | --- |
| `macXplorer.py` | Process identity, `QApplication` setup, event-loop entry point. |
| `core/main_window.py` | Main window, tabs, active pane, menus, settings application, clipboard state, search, navigation actions, and common file operations. |
| `core/widgets.py` | `FilePane`, focus-aware views and path entry, file-system model/proxy, per-pane history, image filtering, and `WorkspaceTab`. |
| `core/plugin_manager.py` | Plugin discovery, validation, initialization, and registration of toolbar/menu actions. |
| `core/theme.py` | Shared dark palette and widget style sheet. |
| `plugins/base.py` | Abstract `BasePlugin` API and immutable `PluginMetadata`. |
| `plugins/diff_plugin.py` | Recursive folder comparison and unified text-file diff dialogs. |
| `plugins/preview_plugin.py` | Preview panel with text, image, and metadata rendering. |
| `plugins/workspace_plugin.py` | Dual-pane toggle and workspace navigation actions. |
| `plugins/settings_plugin.py` | Settings menu action, preference dialog, validation, and persistence. |

## File navigation and views

Each `FilePane` has a `QFileSystemModel` configured for writable file operations, a `QSortFilterProxyModel` for filtering, and two views backed by that proxy: a `QTreeView` for details and a `QListView` for list or icon mode. The root index of each view follows the pane's current folder.

The pane maintains its own navigation history. `WorkspaceTab` owns two panes and their horizontal splitter. The main window's active pane is updated when a pane's view or path field receives focus. The `fileSelected` signal communicates active selection changes to interested plugins, including Preview.

The main search field applies a fixed string filter to each open pane's proxy model. This is a display filter, not an indexed search engine.

## Plugin contract

Plugins subclass `BasePlugin` in `plugins/base.py` and implement:

```python
def initialize(self, core_app: MacXplorer) -> None: ...
def register_toolbar_actions(self) -> Sequence[QAction]: ...
def get_metadata(self) -> PluginMetadata: ...
```

Plugins can optionally implement `register_menu_actions()` and return a mapping of menu titles to action sequences. `PluginMetadata` contains `plugin_id`, `name`, `description`, and `menu`.

The manager validates metadata and verifies registered actions are `QAction` objects. Plugin IDs must be unique. Modules are discovered from the `plugins` package; `plugins/__init__.py` also lists built-ins explicitly for frozen bundle compatibility. New built-in plugins must be added to that list and to `macXplorer.spec` hidden imports when needed by PyInstaller's analysis.

Plugins receive the core window object. They should use its public properties and signals where possible, avoid owning core lifecycle state, and release signal connections or widgets when the core closes.

## Settings and persistence

The core constructs `QSettings("MacExplorer", "MacExplorer")`. These existing identifiers are intentionally retained across the `macXplorer` display-name change so existing preferences remain available. Current keys include:

Branding is centralized in `core/branding.py`. The SVG in `assets/macXplorer.svg` is the editable icon source; the PNG is used at runtime, and the ICNS resource is embedded in the PyInstaller macOS bundle. The About action uses Qt's `AboutRole` so macOS can place it in the application menu. No approved product version, reverse-DNS bundle identifier, signing identity, or support channel is available; the current bundle therefore still uses PyInstaller's default identity/version placeholders and is not release-ready.

| Key | Meaning |
| --- | --- |
| `workspace/leftDirectory` | Left-pane startup location. |
| `workspace/rightDirectory` | Right-pane startup location. |
| `workspace/favorites` | Persisted list of favorite directory paths. |
| `workspace/dualPane` | Whether new workspaces show both panes. |
| `appearance/theme` | `system`, `light`, `dark`, `ocean`, `forest`, `graphite`, `warm_night`, or `terminal`; system follows Qt's reported OS color scheme. |
| `appearance/advancedStyle` | `standard`, `soft_ui`, `neon`, `paper_ui`, `outline`, `borderless`, or `card_based`; composes a Qt-compatible surface treatment with the selected color preset. |
| `appearance/textSize` | `standard`, `large`, or `extra_large` text. |
| `appearance/density` | `comfortable` or `compact` control spacing. |
| `appearance/contrast` | `standard` or `high` contrast. |
| `appearance/colorTreatment` | `standard`, `colorblind`, or `grayscale` palette treatment. |
| Advanced UI theme catalog | Searchable descriptions and implementation notes. Entries with a supported style ID synchronize with `appearance/advancedStyle`; unsupported concepts remain informational. |
| `files/showHidden` | Whether hidden file-system entries are displayed. |
| `files/confirmDelete` | Whether Trash operations require confirmation. |
| `view/showPreview` | Whether the preview panel is visible. |
| `history/recentFiles` | Recently opened local file paths. |

The settings dialog separates general preferences and appearance controls into General and Themes tabs. In the Themes tab, the Advanced style selector and searchable catalog stay synchronized for supported styles. Selecting a supported catalog entry updates the selector; selecting an unsupported entry leaves the active style unchanged. The selected style composes with the color preset, while accessibility choices take precedence for conflicting contrast and color treatments. The dialog validates startup directories before saving and calls `sync()` to persist changes. Its appearance sample renders the selected preset, advanced style, and accessibility options locally without changing the running app. `apply_settings()` updates existing panes, the preview panel, and the application stylesheet after settings are saved. In system mode, the core listens for Qt color-scheme change notifications and refreshes the stylesheet. Themes that require blur, motion, 3D rendering, or another desktop platform's widget system remain informational.

## Clipboard and file operations

macXplorer keeps an internal list of clipboard paths and whether the operation is copy or cut. It also publishes selected paths as local-file URLs through `QClipboard`/`QMimeData`, allowing compatible desktop applications to exchange files. If the internal list is empty, paste attempts to read local URLs from the native clipboard.

Copy uses `shutil.copy2` for files and `shutil.copytree` for directories. Cut uses `shutil.move`. Existing destinations require an explicit replace, skip, or cancel decision. Self-descendant copies are rejected. Folder creation, file creation, and rename validate that the requested name is a single path component.

Moving to Trash is implemented through Finder AppleScript using `/usr/bin/osascript`. Permanent recursive deletion is an internal helper used only to replace an existing destination during paste; it is not the user-facing delete action.

ZIP extraction validates archive member paths and stages extraction in a temporary sibling directory before renaming it into place. ZIP creation checks that the output is not a selected source and does not place the output inside a selected source directory.

## Error handling and security considerations

- File-system, subprocess, and archive failures are logged and shown in dialogs or status messages where the operation has a user-facing flow.
- ZIP member names are checked before extraction to prevent parent-path escapes.
- Item names are treated as paths and validated before creation or rename.
- Clipboard file URLs are restricted to local paths for file operations.
- Finder AppleScript invocation passes the script as an argument to `osascript`; paths are escaped before interpolation.
- The application operates with the current user's macOS file permissions. It does not elevate privileges or bypass macOS privacy controls.
- The project has no dedicated security policy, signed release process, or formal threat model in this repository. Review these before distributing to users.

## Testing and packaging

Tests use `unittest` and set Qt to offscreen mode for automation. The focused suite is:

```bash
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
```

`macXplorer.spec` builds a windowed application bundle named `macXplorer.app`. Plugin modules that PyInstaller cannot detect through dynamic imports are listed in `hiddenimports`.
