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
python macXplorer.py
```

## Repository layout

```text
macXplorer.py          QApplication startup and event-loop entry
core/
  main_window.py       Main window, shared state, file operations, settings
  widgets.py           FilePane, WorkspaceTab, Qt models and views
  plugin_manager.py    Plugin discovery, validation, and action registration
  theme.py             Theme presets and stylesheet composition
  branding.py          App icon, asset lookup, and About dialog
plugins/
  base.py               BasePlugin contract and PluginMetadata
  diff_plugin.py        Folder and file comparison
  preview_plugin.py     Text, image, and metadata preview
  settings_plugin.py    Settings dialog and persistence
  workspace_plugin.py   Dual-pane and workspace actions
  __init__.py           Built-in plugin list for packaged builds
tests/
  test_plugin_manager.py  Qt integration and behavior tests
assets/                   SVG, PNG, and ICNS application icons
docs/                     User, architecture, development, and reference docs
.agents/skills/           Project-scoped repository and implementation skills
macXplorer.spec           PyInstaller bundle definition
```

See [Architecture and Technical Reference](architecture.md) for the verified startup sequence, function-level feature traces, signal/slot map, dependencies, risk notes, Mermaid diagrams, and a prioritized source-reading path.

## Adding a plugin

1. Add a module under `plugins/` and define a concrete subclass of `BasePlugin`.
2. Implement `initialize(core_app)`, `register_toolbar_actions()`, and `get_metadata()`.
3. Return menu actions from `register_menu_actions()` if the plugin needs a menu entry.
4. Use a stable, unique `plugin_id`.
5. Add tests for registration and plugin behavior.
6. Add the module to `plugins/__init__.py` and `macXplorer.spec` if the plugin is built into the frozen application.
7. Run the full test suite.

Keep plugins focused. Core-level state and shared file operations belong in the core; feature-specific interfaces and logic belong in plugins.

## Project skills for coding assistants

Two concise, project-scoped skills guide assistants:

- [Repository guide](../.agents/skills/macxplorer-repository-guide/SKILL.md) explains macXplorer from inspected source and distinguishes verified behavior from assumptions.
- [Approval-first changes](../.agents/skills/macxplorer-approval-first-changes/SKILL.md) clarifies ambiguous behavior and requires a concrete implementation plan to be approved before edits.

The skills are workflow guidance, not a substitute for source inspection, tests, or review. Use the architecture guide as the repository map and verify current source before relying on any prior description.

## Validation

Run tests in offscreen Qt mode:

```bash
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
```

Compile-check Python source:

```bash
python -m compileall -q core plugins macXplorer.py tests
```

There is no project-configured formatter or static type checker at this time. If one is introduced, configure it in the project and document its invocation here.

## Build

Install PyInstaller in the active virtual environment and build:

```bash
python -m pip install pyinstaller
pyinstaller --noconfirm macXplorer.spec
```

The bundle is written to `dist/macXplorer.app`. Test the bundle on a clean macOS account and verify folder privacy permissions, plugin loading, Finder integration, and file operations before release. Configure code signing and notarization separately.

## Contribution expectations

- Keep changes scoped to the documented feature or fix.
- Add or update tests when behavior changes.
- Keep user-facing errors explicit and actionable.
- Do not claim support for an OS version or a feature that has not been tested.
- Confirm the project's license and contribution terms with NanovionLabs before accepting external contributions or redistributing builds.
