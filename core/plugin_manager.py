"""Discovery, initialization, and UI registration for feature plugins."""

import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING

from PyQt6.QtGui import QAction

from plugins import BUILTIN_PLUGIN_MODULES
from plugins.base import BasePlugin, PluginMetadata

if TYPE_CHECKING:
    from core.main_window import MacXplorer

LOGGER = logging.getLogger(__name__)


class PluginManager:
    def __init__(self, core_app: "MacXplorer", toolbar, menus: dict[str, object]):
        self.core_app = core_app
        self.toolbar = toolbar
        self.menus = menus
        self.plugins: dict[str, BasePlugin] = {}
        self.errors: list[str] = []

    def load_plugins(self) -> None:
        for module_name in self._discover_modules():
            try:
                module = importlib.import_module(module_name)
                self._load_module(module)
            except Exception as error:
                message = f"{module_name}: {error}"
                LOGGER.exception("Failed to load plugin module %s", module_name)
                self.errors.append(message)

    @staticmethod
    def _discover_modules() -> list[str]:
        import plugins

        discovered = {
            f"plugins.{module.name}"
            for module in pkgutil.iter_modules(plugins.__path__)
            if not module.name.startswith("_") and module.name != "base"
        }
        discovered.update(BUILTIN_PLUGIN_MODULES)
        return sorted(discovered)

    def _load_module(self, module: ModuleType) -> None:
        plugin_types = [
            candidate
            for _, candidate in inspect.getmembers(module, inspect.isclass)
            if candidate is not BasePlugin
            and issubclass(candidate, BasePlugin)
            and candidate.__module__ == module.__name__
            and not inspect.isabstract(candidate)
        ]
        for plugin_type in plugin_types:
            plugin = plugin_type()
            metadata = plugin.get_metadata()
            self._validate_metadata(metadata)
            if metadata.plugin_id in self.plugins:
                raise ValueError(f"Duplicate plugin id: {metadata.plugin_id}")

            plugin.initialize(self.core_app)
            toolbar_actions = self._validate_actions(
                plugin.register_toolbar_actions(), metadata.name
            )
            menu_actions = plugin.register_menu_actions()

            for action in toolbar_actions:
                self.toolbar.addAction(action)
            for menu_title, actions in menu_actions.items():
                if menu_title not in self.menus:
                    self.menus[menu_title] = self.core_app.menuBar().addMenu(
                        menu_title
                    )
                menu = self.menus[menu_title]
                for action in self._validate_actions(actions, menu_title):
                    menu.addAction(action)

            self.plugins[metadata.plugin_id] = plugin
            LOGGER.info("Loaded plugin %s (%s)", metadata.name, metadata.plugin_id)

    @staticmethod
    def _validate_metadata(metadata: PluginMetadata) -> None:
        if not isinstance(metadata, PluginMetadata):
            raise TypeError("get_metadata() must return PluginMetadata")
        if not metadata.plugin_id.strip() or not metadata.name.strip():
            raise ValueError("Plugin id and name must not be empty")

    @staticmethod
    def _validate_actions(actions, owner: str) -> list[QAction]:
        validated = list(actions)
        invalid = [action for action in validated if not isinstance(action, QAction)]
        if invalid:
            raise TypeError(f"{owner} actions must all be QAction instances")
        return validated

    def get_plugin(self, plugin_id: str) -> BasePlugin | None:
        return self.plugins.get(plugin_id)
