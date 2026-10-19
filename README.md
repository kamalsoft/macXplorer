# macXplorer

macXplorer is a macOS desktop file manager built with Python and PyQt6. It provides tabbed workspaces, a dual-pane browser, file previews, common local file operations, ZIP handling, and an extensible plugin architecture.

The repository and license associate macXplorer with NanovionLabs. The supplied [Nanovian Labs website](https://nanovian.vercel.app/) uses a different spelling; see [About NanovionLabs](docs/about-nanovionlabs.md) for the source distinction and published information.

The macOS app and windows use a custom macXplorer icon and an About panel that identifies the publisher and development status. The application is still under development; its presentation does not imply a release, support, or warranty commitment.

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run macXplorer](#run-macxplorer)
- [Build a macOS application bundle](#build-a-macos-application-bundle)
- [Tests](#tests)
- [Documentation](#documentation)
- [License](#license)
- [Project status](#project-status)

## Features

- Tabbed workspaces, each with two independently navigable file panes.
- Details, list, and icon views; sorting; multi-selection; drag and drop.
- Address-bar navigation, back and forward history, and filtering across open tabs.
- File creation, rename, copy, cut, background paste with progress and cancellation, open, Finder reveal, item information, and move to Trash.
- ZIP archive creation and extraction with path traversal checks.
- Local favorites, recent files, common macOS folders, and mounted volumes.
- Text, image, and file metadata previews.
- Folder and text-file comparison through the Diff plugin.
- Open macOS Terminal in the active pane's current folder.
- Persistent preferences for macOS-oriented system, light, dark, ocean, forest, graphite, warm night, and terminal appearances, plus high contrast, text size, density, and color treatment. Settings has separate General and Themes tabs, including a searchable catalog of advanced UI design concepts.

The app works with local and mounted paths exposed through macOS. It does not currently provide cloud-provider integrations, Windows shell features, or a full content-indexed search service. The search field filters the file model in open workspaces.

## Requirements

- macOS
- Python 3.10 or newer
- PyQt6

Python and PyQt6 versions are not pinned in a dependency manifest in this repository. For a reproducible deployment, use a project-managed environment and record tested versions before publishing a release.

## Installation

From the repository root:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install PyQt6
```

Run the application:

```bash
python macXplorer.py
```

macOS may request access to folders protected by privacy controls. Grant the application or the terminal running it the required access in **System Settings > Privacy & Security**.

## Build a macOS application bundle

Install PyInstaller in the active environment and build from the repository root:

```bash
python -m pip install pyinstaller
pyinstaller --noconfirm macXplorer.spec
```

The spec defines a windowed `macXplorer.app` bundle under `dist/`. Sign, notarize, and test the resulting bundle on the target macOS versions before distributing it. Packaging does not automatically provide a signing identity, notarization, updater, or installer.

## Tests

Run the test suite in headless Qt mode:

```bash
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
```

The tests cover plugin startup, previews, comparisons, workspace behavior, settings persistence, tab navigation, file clipboard operations, image filtering, and ZIP safety checks.

## Documentation

- [User guide](docs/user-guide.md): navigation, file operations, settings, and keyboard shortcuts.
- [Architecture and technical reference](docs/architecture.md): verified repository structure, startup and feature traces, signal/slot map, plugin lifecycle, dependency map, risks, and learning path.
- [Development guide](docs/development.md): source map, local setup, plugin development, tests, packaging, and contribution checks.
- [References](docs/references.md): official Python, Qt, PyQt, Apple, and project attribution references.
- [About NanovionLabs](docs/about-nanovionlabs.md): company attribution and verified-information boundary.
- [License policy](docs/license-policy.md): plain-language summary of the MIT License.
- Project-scoped coding-assistant skills are documented in the [development guide](docs/development.md#project-skills-for-coding-assistants).

## License

macXplorer is distributed under the [MIT License](LICENSE). See the [license policy](docs/license-policy.md) for a plain-language summary. Third-party dependencies may have separate license terms.

## Project status

macXplorer is actively developed. 

## Disclaimer

macXplorer is under development and is provided "as is," without guarantees of availability, fitness, or data safety. Use of the application is at the user's own risk. The user is responsible for evaluating the application before use, maintaining backups, and any consequences of using it. The developer, its associates, and contributors make no commitment to provide support and are not responsible for loss or damage arising from use of the application, to the extent permitted by applicable law.