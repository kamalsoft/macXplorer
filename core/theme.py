"""Shared dark theme for the application and its plugins."""

DARK_THEME = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: "Helvetica Neue";
    font-size: 13px;
}

QTreeView, QTableWidget {
    background-color: #252526;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    color: #cccccc;
    gridline-color: #3c3c3c;
    show-decoration-selected: 1;
    alternate-background-color: #29292a;
}

QTreeView::item, QTableWidget::item {
    padding: 4px;
}

QTreeView::item:hover, QTableWidget::item:hover {
    background-color: #2a2d2e;
}

QTreeView::item:selected, QTableWidget::item:selected {
    background-color: #094771;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #9cdcfe;
    padding: 5px;
    border: none;
    border-right: 1px solid #3c3c3c;
    border-bottom: 1px solid #3c3c3c;
    font-weight: bold;
}

QLineEdit, QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #3c3c3c;
    border-radius: 4px;
    padding: 4px 8px;
    color: #d4d4d4;
    selection-background-color: #094771;
}

QTextEdit, QPlainTextEdit {
    background-color: #1e1e1e;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    color: #ce9178;
    selection-background-color: #094771;
    font-family: "Menlo";
}

QToolBar {
    background-color: #2d2d2d;
    border: none;
    border-bottom: 1px solid #3c3c3c;
    spacing: 8px;
    padding: 4px;
}

QToolButton {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px 8px;
    color: #ffffff;
}

QToolButton:hover, QPushButton:hover {
    background-color: #4e4e4e;
}

QToolButton:pressed, QPushButton:pressed {
    background-color: #007acc;
}

QLabel {
    color: #cccccc;
}

QSplitter::handle {
    background-color: #3c3c3c;
}

QPushButton {
    background-color: #333333;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 6px 12px;
    color: #ffffff;
    font-weight: bold;
}

QPushButton:default {
    border-color: #007acc;
}

QMenuBar, QMenu {
    background-color: #2d2d2d;
    color: #d4d4d4;
}

QMenuBar::item:selected, QMenu::item:selected {
    background-color: #094771;
}

QMenu::separator {
    height: 1px;
    background: #3c3c3c;
    margin: 4px 8px;
}

QStatusBar {
    background-color: #252526;
    color: #cccccc;
}

QScrollBar:vertical {
    background: #1e1e1e;
    width: 12px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #555555;
    min-height: 24px;
    border-radius: 5px;
}

QScrollBar:horizontal {
    background: #1e1e1e;
    height: 12px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #555555;
    min-width: 24px;
    border-radius: 5px;
}

QScrollBar::add-line, QScrollBar::sub-line {
    width: 0;
    height: 0;
}
"""
