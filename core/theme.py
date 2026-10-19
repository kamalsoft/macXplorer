"""Application styles for built-in appearance presets."""

from typing import NamedTuple

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

_DARK_BASE = {
    "window": "#1e1e1e",
    "text": "#d4d4d4",
    "surface": "#252526",
    "border": "#3c3c3c",
    "secondary_text": "#cccccc",
    "alternate": "#29292a",
    "hover": "#2a2d2e",
    "selection": "#094771",
    "header": "#2d2d2d",
    "header_text": "#9cdcfe",
    "input": "#2d2d2d",
    "editor": "#1e1e1e",
    "editor_text": "#ce9178",
    "toolbar": "#2d2d2d",
    "button": "#333333",
    "button_border": "#555555",
    "button_text": "#ffffff",
    "button_hover": "#4e4e4e",
    "accent": "#007acc",
    "scrollbar": "#555555",
}

_LIGHT_BASE = {
    "window": "#f5f5f7",
    "text": "#242424",
    "surface": "#ffffff",
    "border": "#c8c8cc",
    "secondary_text": "#333333",
    "alternate": "#eeeeee",
    "hover": "#e5f1fb",
    "selection": "#0a64ad",
    "header": "#e9e9ed",
    "header_text": "#242424",
    "input": "#ffffff",
    "editor": "#ffffff",
    "editor_text": "#242424",
    "toolbar": "#eeeeF2",
    "button": "#e7e7eb",
    "button_border": "#b8b8be",
    "button_text": "#242424",
    "button_hover": "#d8e8f5",
    "accent": "#0a64ad",
    "scrollbar": "#aaaaaf",
}

THEME_OPTIONS = (
    ("macOS Adaptive (System)", "system"),
    ("macOS Light", "light"),
    ("macOS Dark", "dark"),
    ("Ocean", "ocean"),
    ("Forest", "forest"),
    ("Graphite", "graphite"),
    ("Warm Night", "warm_night"),
    ("Terminal", "terminal"),
)


class AdvancedThemeInfo(NamedTuple):
    name: str
    category: str
    description: str
    implementation_note: str


ADVANCED_THEME_CATALOG = (
    AdvancedThemeInfo(
        "Glassmorphism",
        "Transparency and depth",
        "Uses translucent panels layered over a visible background.",
        "Informational only: the app does not render backdrop blur or glass transparency.",
    ),
    AdvancedThemeInfo(
        "Liquid Glass",
        "Transparency and depth",
        "A fluid glass-like surface treatment with responsive highlights and refraction.",
        "Informational only: refraction, dynamic highlights, and liquid surfaces are not implemented.",
    ),
    AdvancedThemeInfo(
        "Frosted Glass",
        "Transparency and depth",
        "Softens content behind translucent panels with a frosted blur.",
        "Informational only: Qt stylesheet themes do not provide the required backdrop blur here.",
    ),
    AdvancedThemeInfo(
        "Aurora Gradient",
        "Color and light",
        "Uses luminous, flowing color bands inspired by aurora light.",
        "Informational only: animated gradient backgrounds are not part of the current theme engine.",
    ),
    AdvancedThemeInfo(
        "Mesh Gradient",
        "Color and light",
        "Blends several color points into a continuous, multi-dimensional gradient.",
        "Informational only: mesh-gradient rendering is not implemented.",
    ),
    AdvancedThemeInfo(
        "Holographic",
        "Color and light",
        "Applies iridescent, color-shifting highlights to surfaces.",
        "Informational only: dynamic holographic materials are not implemented.",
    ),
    AdvancedThemeInfo(
        "Neon Glow",
        "Color and light",
        "Pairs dark surfaces with bright accents and luminous edge treatments.",
        "Informational only: the current app has no glow or animated-light rendering.",
    ),
    AdvancedThemeInfo(
        "Ambient UI",
        "Adaptive interfaces",
        "Adapts interface lighting and tone to the surrounding environment or context.",
        "Informational only: ambient sensing and context-adaptive lighting are not implemented.",
    ),
    AdvancedThemeInfo(
        "Soft UI",
        "Surface treatments",
        "Uses gentle contrast and soft raised or recessed surface cues.",
        "Catalog concept only: a Soft UI appearance preset is not currently available.",
    ),
    AdvancedThemeInfo(
        "3D UI",
        "Spatial and dimensional",
        "Uses perspective, depth, and three-dimensional controls or transitions.",
        "Informational only: the app uses standard 2D Qt widgets and has no 3D renderer.",
    ),
    AdvancedThemeInfo(
        "Spatial UI",
        "Spatial and dimensional",
        "Places controls and content in a spatial interface with depth-aware interaction.",
        "Informational only: spatial computing interaction is not supported by this desktop app.",
    ),
    AdvancedThemeInfo(
        "Skeuomorphic 3D",
        "Spatial and dimensional",
        "Combines physical-object metaphors, material textures, and dimensional shading.",
        "Informational only: textured materials and 3D rendering are not implemented.",
    ),
    AdvancedThemeInfo(
        "Paper UI",
        "Surface treatments",
        "Suggests paper surfaces with restrained color, texture, and layered content.",
        "Catalog concept only: paper textures and a dedicated Paper UI preset are not available.",
    ),
    AdvancedThemeInfo(
        "Outline UI",
        "Surface treatments",
        "Defines interface regions with clear outlines rather than filled surfaces.",
        "Catalog concept only: an Outline UI preset is not currently available.",
    ),
    AdvancedThemeInfo(
        "Borderless UI",
        "Surface treatments",
        "Reduces visible borders and relies on spacing and hierarchy to separate content.",
        "Catalog concept only: a Borderless UI preset is not currently available.",
    ),
    AdvancedThemeInfo(
        "Card-Based UI",
        "Layout patterns",
        "Groups related content into distinct cards for scanning and organization.",
        "Informational only: adopting this pattern requires a layout redesign, not just a color preset.",
    ),
    AdvancedThemeInfo(
        "Bento Grid",
        "Layout patterns",
        "Arranges content into a modular grid of differently sized, related panels.",
        "Informational only: the file explorer does not currently use a bento-grid layout.",
    ),
    AdvancedThemeInfo(
        "Floating UI",
        "Layout patterns",
        "Uses detached, layered controls or panels that float above the main content.",
        "Informational only: floating overlay surfaces are not implemented.",
    ),
    AdvancedThemeInfo(
        "Layered UI",
        "Layout patterns",
        "Communicates hierarchy through overlapping surfaces and elevation.",
        "Catalog concept only: layered elevation is not a selectable appearance preset.",
    ),
    AdvancedThemeInfo(
        "Motion-First UI",
        "Motion and interaction",
        "Uses animation as a primary way to communicate state and guide interaction.",
        "Informational only: a motion system is not implemented; reduced-motion behavior is not configurable.",
    ),
    AdvancedThemeInfo(
        "Parallax UI",
        "Motion and interaction",
        "Moves foreground and background at different rates to create depth during scrolling.",
        "Informational only: parallax behavior is not implemented.",
    ),
    AdvancedThemeInfo(
        "Immersive UI",
        "Motion and interaction",
        "Uses a full-screen, content-focused environment with minimal surrounding chrome.",
        "Informational only: a dedicated immersive presentation mode is not implemented.",
    ),
    AdvancedThemeInfo(
        "Generative / AI-Adaptive UI",
        "Adaptive interfaces",
        "Uses AI or generative rules to adapt layout, content, or styling to a user or task.",
        "Informational only: the app does not use AI to generate or adapt its interface.",
    ),
)

TEXT_SIZE_OPTIONS = (
    ("Standard", "standard"),
    ("Large", "large"),
    ("Extra Large", "extra_large"),
)
DENSITY_OPTIONS = (("Comfortable", "comfortable"), ("Compact", "compact"))
CONTRAST_OPTIONS = (("Standard", "standard"), ("High Contrast", "high"))
COLOR_TREATMENT_OPTIONS = (
    ("Standard", "standard"),
    ("Colorblind-friendly accents", "colorblind"),
    ("Grayscale", "grayscale"),
)

THEME_COLORS = {
    "light": _LIGHT_BASE,
    "dark": _DARK_BASE,
    "ocean": {
        **_DARK_BASE,
        "window": "#111c2b",
        "text": "#dce8f5",
        "surface": "#17263a",
        "border": "#2c4561",
        "secondary_text": "#c4d8ed",
        "alternate": "#1b2d43",
        "hover": "#25415e",
        "selection": "#176b91",
        "header": "#182a40",
        "header_text": "#9fe3ed",
        "input": "#17263a",
        "editor": "#111c2b",
        "editor_text": "#c1e8e6",
        "toolbar": "#182a40",
        "button": "#203751",
        "button_border": "#3b5877",
        "button_hover": "#2b4b69",
        "accent": "#1596b7",
        "scrollbar": "#496986",
    },
    "forest": {
        **_DARK_BASE,
        "window": "#17211c",
        "text": "#e0e9e1",
        "surface": "#1d2b23",
        "border": "#394c3f",
        "secondary_text": "#d0dfd2",
        "alternate": "#223329",
        "hover": "#2d4535",
        "selection": "#356c4a",
        "header": "#202e25",
        "header_text": "#b5dfb8",
        "input": "#1d2b23",
        "editor": "#17211c",
        "editor_text": "#c6e0bd",
        "toolbar": "#202e25",
        "button": "#2b3d30",
        "button_border": "#4c6252",
        "button_hover": "#3a5342",
        "accent": "#579363",
        "scrollbar": "#617869",
    },
    "graphite": {
        **_DARK_BASE,
        "window": "#242424",
        "text": "#eeeeee",
        "surface": "#2b2b2b",
        "border": "#4b4b4b",
        "secondary_text": "#dddddd",
        "alternate": "#303030",
        "hover": "#3a3a3a",
        "selection": "#555555",
        "header": "#303030",
        "header_text": "#eeeeee",
        "input": "#2b2b2b",
        "editor": "#242424",
        "editor_text": "#eeeeee",
        "toolbar": "#303030",
        "button": "#3b3b3b",
        "button_border": "#5c5c5c",
        "button_hover": "#4a4a4a",
        "accent": "#777777",
        "scrollbar": "#686868",
    },
    "warm_night": {
        **_DARK_BASE,
        "window": "#211b1a",
        "text": "#f1e5d7",
        "surface": "#2a211e",
        "border": "#57443a",
        "secondary_text": "#e0cdbb",
        "alternate": "#302521",
        "hover": "#443126",
        "selection": "#744426",
        "selection_text": "#fff7e8",
        "header": "#30241f",
        "header_text": "#f3c891",
        "input": "#2a211e",
        "editor": "#211b1a",
        "editor_text": "#f0d5b4",
        "toolbar": "#30241f",
        "button": "#3c2c24",
        "button_border": "#665041",
        "button_hover": "#523a2c",
        "accent": "#d38a43",
        "scrollbar": "#705844",
    },
    "terminal": {
        **_DARK_BASE,
        "window": "#101410",
        "text": "#d7e8d2",
        "surface": "#151c16",
        "border": "#3c4a3b",
        "secondary_text": "#c6dac0",
        "alternate": "#192119",
        "hover": "#263426",
        "selection": "#29492d",
        "selection_text": "#eaffdf",
        "header": "#182019",
        "header_text": "#9fdb88",
        "input": "#151c16",
        "editor": "#101410",
        "editor_text": "#b7df9b",
        "toolbar": "#182019",
        "button": "#222e22",
        "button_border": "#465744",
        "button_hover": "#304331",
        "accent": "#75bd58",
        "scrollbar": "#52674d",
    },
}


def system_theme_name(application: QApplication) -> str:
    """Return the OS color scheme, using the application palette if unknown."""
    style_hints = application.styleHints()
    color_scheme = getattr(Qt, "ColorScheme", None)
    get_scheme = getattr(style_hints, "colorScheme", None)
    if color_scheme is not None and get_scheme is not None:
        scheme = get_scheme()
        if scheme == color_scheme.Dark:
            return "dark"
        if scheme == color_scheme.Light:
            return "light"
    window_color = application.palette().color(QPalette.ColorRole.Window)
    return "dark" if window_color.lightness() < 128 else "light"


def theme_stylesheet(
    theme: str,
    *,
    text_size: str = "standard",
    density: str = "comfortable",
    contrast: str = "standard",
    color_treatment: str = "standard",
) -> str:
    """Build the application stylesheet for a preset and accessibility choices."""
    if theme not in THEME_COLORS:
        raise ValueError(f"Unknown application theme: {theme}")
    if text_size not in {value for _, value in TEXT_SIZE_OPTIONS}:
        raise ValueError(f"Unknown text size: {text_size}")
    if density not in {value for _, value in DENSITY_OPTIONS}:
        raise ValueError(f"Unknown interface density: {density}")
    if contrast not in {value for _, value in CONTRAST_OPTIONS}:
        raise ValueError(f"Unknown contrast setting: {contrast}")
    if color_treatment not in {value for _, value in COLOR_TREATMENT_OPTIONS}:
        raise ValueError(f"Unknown color treatment: {color_treatment}")

    colors = dict(THEME_COLORS[theme])
    colors.setdefault("selection_text", "#ffffff")
    dark = QColor(colors["window"]).lightness() < 128
    if contrast == "high":
        colors.update(
            {
                "window": "#000000" if dark else "#ffffff",
                "surface": "#000000" if dark else "#ffffff",
                "text": "#ffffff" if dark else "#000000",
                "secondary_text": "#ffffff" if dark else "#000000",
                "border": "#ffffff" if dark else "#000000",
                "header": "#000000" if dark else "#ffffff",
                "header_text": "#ffffff" if dark else "#000000",
                "input": "#000000" if dark else "#ffffff",
                "editor": "#000000" if dark else "#ffffff",
                "editor_text": "#ffffff" if dark else "#000000",
                "selection": "#ffff00" if dark else "#000080",
                "selection_text": "#000000" if dark else "#ffffff",
                "button_border": "#ffffff" if dark else "#000000",
            }
        )
    if color_treatment == "colorblind":
        colors["accent"] = "#ffbf47" if dark else "#a64b00"
    elif color_treatment == "grayscale":
        for name, value in colors.items():
            color = QColor(value)
            luminance = round(
                color.red() * 0.2126
                + color.green() * 0.7152
                + color.blue() * 0.0722
            )
            colors[name] = QColor(luminance, luminance, luminance).name()

    font_size = {"standard": 13, "large": 15, "extra_large": 18}[text_size]
    compact = density == "compact"
    item_padding = 2 if compact else 6
    control_padding = "3px 6px" if compact else "6px 10px"
    border_width = 2 if contrast == "high" else 1
    focus_width = 3 if contrast == "high" else 2
    return f"""
QMainWindow, QWidget {{
    background-color: {colors["window"]};
    color: {colors["text"]};
    font-family: "Helvetica Neue";
    font-size: {font_size}px;
}}

QTreeView, QListWidget, QTableWidget {{
    background-color: {colors["surface"]};
    border: {border_width}px solid {colors["border"]};
    border-radius: 6px;
    color: {colors["secondary_text"]};
    gridline-color: {colors["border"]};
    show-decoration-selected: 1;
    alternate-background-color: {colors["alternate"]};
}}

QTreeView::item, QListWidget::item, QTableWidget::item {{
    padding: {item_padding}px;
}}
QTreeView::item:hover, QListWidget::item:hover, QTableWidget::item:hover {{
    background-color: {colors["hover"]};
}}
QTreeView::item:selected, QListWidget::item:selected, QTableWidget::item:selected {{
    background-color: {colors["selection"]};
    color: {colors["selection_text"]};
    border: {focus_width}px solid {colors["accent"] if color_treatment == "colorblind" or contrast == "high" else colors["selection"]};
}}

QHeaderView::section {{
    background-color: {colors["header"]};
    color: {colors["header_text"]};
    padding: 5px;
    border: none;
    border-right: 1px solid {colors["border"]};
    border-bottom: 1px solid {colors["border"]};
    font-weight: bold;
}}

QLineEdit, QComboBox {{
    background-color: {colors["input"]};
    border: {border_width}px solid {colors["border"]};
    border-radius: 4px;
    padding: {control_padding};
    color: {colors["text"]};
    selection-background-color: {colors["selection"]};
}}

QTextEdit, QPlainTextEdit {{
    background-color: {colors["editor"]};
    border: {border_width}px solid {colors["border"]};
    border-radius: 6px;
    color: {colors["editor_text"]};
    selection-background-color: {colors["selection"]};
    font-family: "Menlo";
}}

QToolBar {{
    background-color: {colors["toolbar"]};
    border: none;
    border-bottom: 1px solid {colors["border"]};
    spacing: 8px;
    padding: {control_padding};
}}
QToolButton {{
    background-color: {colors["button"]};
    border: {border_width}px solid {colors["button_border"]};
    border-radius: 4px;
    padding: {control_padding};
    color: {colors["button_text"]};
}}
QToolButton:hover, QPushButton:hover {{
    background-color: {colors["button_hover"]};
}}
QToolButton:pressed, QPushButton:pressed {{
    background-color: {colors["accent"]};
}}

QLabel {{ color: {colors["secondary_text"]}; }}
QSplitter::handle {{ background-color: {colors["border"]}; }}
QPushButton {{
    background-color: {colors["button"]};
    border: {border_width}px solid {colors["button_border"]};
    border-radius: 4px;
    padding: {control_padding};
    color: {colors["button_text"]};
    font-weight: bold;
}}
QPushButton:default, QLineEdit:focus, QComboBox:focus, QPushButton:focus,
QTreeView:focus, QListWidget:focus, QTableWidget:focus {{
    border: {focus_width}px solid {colors["accent"]};
}}
QMenuBar, QMenu {{
    background-color: {colors["header"]};
    color: {colors["text"]};
}}
QMenuBar::item:selected, QMenu::item:selected {{
    background-color: {colors["selection"]};
}}
QMenu::separator {{
    height: 1px;
    background: {colors["border"]};
    margin: 4px 8px;
}}
QStatusBar {{
    background-color: {colors["surface"]};
    color: {colors["secondary_text"]};
}}
QScrollBar:vertical {{
    background: {colors["window"]};
    width: 12px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {colors["scrollbar"]};
    min-height: 24px;
    border-radius: 5px;
}}
QScrollBar:horizontal {{
    background: {colors["window"]};
    height: 12px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background: {colors["scrollbar"]};
    min-width: 24px;
    border-radius: 5px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
"""
