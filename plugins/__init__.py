"""Built-in and dynamically discovered explorer plugins."""

# Kept as a fallback for frozen application bundles, where package iteration
# cannot always enumerate modules from the executable archive.
BUILTIN_PLUGIN_MODULES = (
    "plugins.diff_plugin",
    "plugins.preview_plugin",
    "plugins.settings_plugin",
    "plugins.terminal_plugin",
    "plugins.workspace_plugin",
)
