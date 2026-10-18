# Development Guide

## Environment

Use macOS with Python 3.10 or newer and PyQt6. The repository currently has no `requirements.txt`, `pyproject.toml`, or other dependency lock file. Create an isolated environment and install the runtime dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install PyQt6
```

Launch from the repository root so Python can import `core` and `plugins`:

```bash
python explorer.py
```

## Repository layout

```text
core/                 Application shell, reusable widgets, plugin manager, theme
plugins/              Built-in plugins and plugin contract
tests/                unittest integration and behavior tests
docs/                 User, architecture, development, and reference documents
explorer.py           Application entry point
MacExplorer.spec      PyInstaller application-bundle definition
```

## Adding a plugin

1. Add a module under `plugins/` and define a concrete subclass of `BasePlugin`.
2. Implement `initialize(core_app)`, `register_toolbar_actions()`, and `get_metadata()`.
3. Return menu actions from `register_menu_actions()` if the plugin needs a menu entry.
4. Use a stable, unique `plugin_id`.
5. Add tests for registration and plugin behavior.
6. Add the module to `plugins/__init__.py` and `MacExplorer.spec` if the plugin is built into the frozen application.
7. Run the full test suite.

Keep plugins focused. Core-level state and shared file operations belong in the core; feature-specific interfaces and logic belong in plugins.

## Validation

Run tests in offscreen Qt mode:

```bash
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
```

Compile-check Python source:

```bash
python -m compileall -q core plugins explorer.py tests
```

There is no project-configured formatter or static type checker at this time. If one is introduced, configure it in the project and document its invocation here.

## Build

Install PyInstaller in the active virtual environment and build:

```bash
python -m pip install pyinstaller
pyinstaller --noconfirm MacExplorer.spec
```

The bundle is written to `dist/MacExplorer.app`. Test the bundle on a clean macOS account and verify folder privacy permissions, plugin loading, Finder integration, and file operations before release. Configure code signing and notarization separately.

## Contribution expectations

- Keep changes scoped to the documented feature or fix.
- Add or update tests when behavior changes.
- Keep user-facing errors explicit and actionable.
- Do not claim support for an OS version or a feature that has not been tested.
- Confirm the project's license and contribution terms with NanovionLabs before accepting external contributions or redistributing builds.
