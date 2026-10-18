# macXplorer

macXplorer is a macOS desktop file manager built with Python and PyQt6. It provides tabbed workspaces, a dual-pane browser, file previews, common local file operations, ZIP handling, and an extensible plugin architecture.

macXplorer is a NanovionLabs application. See [About NanovionLabs](docs/about-nanovionlabs.md) for the project attribution and the company information available in this repository.

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run macXplorer](#run-macxplorer)
- [Build a macOS application bundle](#build-a-macos-application-bundle)
- [Tests](#tests)
- [Documentation](#documentation)
- [Project status](#project-status)

## Features

- Tabbed workspaces, each with two independently navigable file panes.
- Details, list, and icon views; sorting; multi-selection; drag and drop.
- Address-bar navigation, back and forward history, and filtering across open tabs.
- File creation, rename, copy, cut, paste, open, Finder reveal, item information, and move to Trash.
- ZIP archive creation and extraction with path traversal checks.
- Local favorites, recent files, common macOS folders, and mounted volumes.
- Text, image, and file metadata previews.
- Folder and text-file comparison through the Diff plugin.
- Persistent preferences for startup folders, favorites, hidden files, delete confirmation, preview visibility, and dual-pane startup.

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
- [Architecture and technical reference](docs/architecture.md): component boundaries, plugin lifecycle, settings, file operations, and extension contract.
- [Development guide](docs/development.md): local setup, tests, packaging, and contribution checks.
- [References](docs/references.md): official Python, Qt, PyQt, Apple, and project attribution references.
- [About NanovionLabs](docs/about-nanovionlabs.md): company attribution and verified-information boundary.

## Project status

macXplorer is actively developed. The repository currently has no published version number, release policy, support commitment, or declared software license. Confirm these items with the project owner before distributing the application or accepting external contributions.