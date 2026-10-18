"""Plugin contracts and metadata types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping, Sequence, TYPE_CHECKING

from PyQt6.QtGui import QAction

if TYPE_CHECKING:
    from core.main_window import MacXplorer


@dataclass(frozen=True)
class PluginMetadata:
    plugin_id: str
    name: str
    description: str
    menu: str


class BasePlugin(ABC):
    """Base class for explorer plugins loaded by :class:`PluginManager`."""

    @abstractmethod
    def initialize(self, core_app: "MacXplorer") -> None:
        """Attach the plugin to the core application."""

    @abstractmethod
    def register_toolbar_actions(self) -> Sequence[QAction]:
        """Return actions to add to the main toolbar."""

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return stable identity and display information for this plugin."""

    def register_menu_actions(self) -> Mapping[str, Sequence[QAction]]:
        """Return actions grouped by menu title."""
        return {}
