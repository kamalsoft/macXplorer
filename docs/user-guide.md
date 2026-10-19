# macXplorer User Guide

## Overview

macXplorer presents local and mounted file-system locations in tabbed workspaces. Each workspace contains a left pane and an optional right pane. A preview panel can display supported text, image, and metadata content.

## Workspaces and navigation

- Use **File > New Tab** to open a workspace. A new tab starts at the active pane's current folder.
- Use the tab close button or **File > Close Tab** to close a tab. Closing the final tab creates a replacement workspace.
- Double-click a folder to navigate into it. Double-click a file to open it with the macOS default application.
- Enter a folder path in a pane's path field and press Return to navigate.
- Use **View > Back**, **Forward**, **Up**, or **Home** for navigation.
- Use **View > Toggle Dual Pane** to show or hide the right pane.
- Use **Go > Favorites**, **Locations**, and **Recent Files** to jump to saved or commonly used locations.
- **Browse Photos** opens the Pictures folder, or asks for a folder if Pictures is unavailable, then enables image filtering and icon view.

The search field applies a case-insensitive filename filter to the file panes in every open tab. It filters the file model; it does not search file contents or index the entire disk.

## Views and selection

The View menu provides:

| View | Description |
| --- | --- |
| Details | File-system table with name and metadata columns. |
| List | Compact list of entries. |
| Icons | Icon-oriented grid. |
| Show Images Only | Filters visible entries to supported image filename patterns. |

Both pane views support extended selection. Drag-and-drop is enabled by the Qt item views and uses Qt's file-system model behavior. Copy, cut, and paste use local file URLs on the system clipboard.

## File operations

| Operation | Where to find it |
| --- | --- |
| Create folder or empty file | File menu |
| Rename selected item | File menu |
| Copy, cut, paste, select all | Edit menu or file context menu |
| Open selected file or folder | Tools menu or file context menu |
| Reveal an item in Finder | Tools menu or file context menu |
| View item information | Tools menu or file context menu |
| Move selected items to Trash | File menu, Edit menu, or context menu |
| Create ZIP archive | Tools menu |
| Extract selected ZIP archive | Tools menu |

Delete confirmation is enabled by default. The Trash action uses macOS Finder through `osascript`. It does not perform permanent deletion. Errors are reported to the user.

Copy and cut support multiple selected items. If a destination already contains an item with the same name, macXplorer asks whether to replace, skip, or cancel. Copying a folder into itself or one of its descendants is rejected.

ZIP extraction rejects entries with absolute paths or parent-directory traversal and extracts to a temporary staging directory before publishing the result. Archive creation avoids including the output archive within a selected source directory.

## Preferences

Open **File > Explorer Settings…** to configure:

- Left and right startup folders.
- Favorites.
- Hidden-file visibility.
- Delete confirmation.
- Preview panel visibility.
- Whether new workspaces start with both panes visible.
- Appearance presets: macOS Adaptive (System), macOS Light, macOS Dark, Ocean, Forest, Graphite, Warm Night, and Terminal. The Adaptive preset follows macOS appearance changes while the app is open.
- Accessibility options: Standard or High Contrast, Standard/Large/Extra Large text, Comfortable or Compact density, and Standard/Colorblind-friendly accents/Grayscale color treatment.
- An appearance preview shows sample file items, an input field, and an action button. It reflects both the selected preset and accessibility options. Changing options updates only the preview; save the settings to apply them.

macXplorer uses Qt's native keyboard and accessibility interfaces. It does not add custom blur, animation, 3D effects, or platform-specific themes for Windows, GNOME, Android, or web browsers.

Preferences continue to use the existing Qt `QSettings` organization and application identifiers (`MacExplorer`) so renaming the app does not discard saved settings. Settings changes are applied after saving.

## Keyboard shortcuts

Shortcuts are interpreted by Qt and may be presented with macOS modifier labels in the native menu.

| Action | Shortcut |
| --- | --- |
| New tab | Command+T |
| New window | Command+N |
| New folder | Command+Shift+N |
| Close tab | Command+W |
| Rename selected item | F2 |
| Copy | Command+C |
| Cut | Command+X |
| Paste | Command+V |
| Select all | Command+A |
| Back | Command+[ |
| Forward | Command+] |
| Focus path field | Command+L |
| Focus search field | Command+F |
| Toggle dual pane | Command+Shift+D |
| Toggle dual pane (Workspace plugin) | Command+D |
| Parent directory | Command+Up |
| Home directory | Command+Shift+H |
| Open selected item | Command+O |
| Get Info | Command+I |

Qt maps the `Ctrl` shortcut modifier to the Command key on macOS. The Workspace plugin adds the pane and directory shortcuts shown above.

## Known boundaries

- File listings use `QFileSystemModel`; they reflect local volumes and mounted locations available to the current macOS user.
- The search field filters names in the displayed file model and does not search file contents.
- Preview supports a defined set of image and text extensions. Text files larger than 100 KiB are not previewed as text.
- Recent files are added when opening a file through macXplorer succeeds. The list is local application history.
- The app does not currently implement cloud synchronization, Windows-specific shell extensions, a recycle-bin browser, operation undo, or a full archive manager.
