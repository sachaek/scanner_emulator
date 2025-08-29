"""Единая тема оформления и базовые классы окон/диалогов."""

from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtCore import Qt
import ctypes
import platform
import json
import os


QSS_DARK = """
QWidget {
    background-color: #121212;
    color: #E0E0E0;
}
QLabel { color: #E0E0E0; }
QLineEdit {
    background: #1E1E1E;
    color: #E0E0E0;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: #2F6FED;
    selection-color: #FFFFFF;
}
QLineEdit:focus { border: 1px solid #4F8CFF; }

QPushButton {
    background: #2A2A2A;
    color: #E0E0E0;
    border: 1px solid #3A3A3A;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton:hover { background: #323232; }
QPushButton:pressed { background: #262626; }
QPushButton:disabled {
    color: #777777;
    background: #1C1C1C;
    border-color: #2A2A2A;
}

QMessageBox { background-color: #1A1A1A; }

QMenuBar {
    background-color: #171717;
    color: #E0E0E0;
    border-bottom: 1px solid #2A2A2A;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 8px;
    margin: 0 2px;
    border-radius: 4px;
}
QMenuBar::item:selected { background: #2A2A2A; }

QMenu {
    background-color: #1B1B1B;
    color: #E0E0E0;
    border: 1px solid #2A2A2A;
}
QMenu::item { padding: 6px 18px; }
QMenu::item:selected { background-color: #2F2F2F; }

QSpinBox, QDoubleSpinBox {
    background: #1E1E1E;
    color: #E0E0E0;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 4px 6px;
    selection-background-color: #2F6FED;
    selection-color: #FFFFFF;
}
QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #4F8CFF; }
"""

QSS_LIGHT = """
QWidget {
    background-color: #F7F7F7;
    color: #1A1A1A;
}
QLabel { color: #1A1A1A; }
QLineEdit {
    background: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #C8C8C8;
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: #2F6FED;
    selection-color: #FFFFFF;
}
QLineEdit:focus { border: 1px solid #3D6BFF; }

QPushButton {
    background: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #C8C8C8;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton:hover { background: #F0F0F0; }
QPushButton:pressed { background: #E8E8E8; }
QPushButton:disabled {
    color: #9B9B9B;
    background: #F3F3F3;
    border-color: #DDDDDD;
}

QMessageBox { background-color: #FFFFFF; }

QMenuBar {
    background-color: #F1F1F1;
    color: #1A1A1A;
    border-bottom: 1px solid #DDDDDD;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 8px;
    margin: 0 2px;
    border-radius: 4px;
}
QMenuBar::item:selected { background: #E8E8E8; }

QMenu {
    background-color: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #DDDDDD;
}
QMenu::item { padding: 6px 18px; }
QMenu::item:selected { background-color: #EFEFEF; }

QSpinBox, QDoubleSpinBox {
    background: #FFFFFF;
    color: #1A1A1A;
    border: 1px solid #C8C8C8;
    border-radius: 6px;
    padding: 4px 6px;
    selection-background-color: #2F6FED;
    selection-color: #FFFFFF;
}
QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #3D6BFF; }
"""

_THEME_STORE = os.path.join(os.path.dirname(__file__), 'ui_theme.json')


def _load_theme_name() -> str:
    if os.path.exists(_THEME_STORE):
        try:
            with open(_THEME_STORE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    name = data.get('theme')
                    if name in ('dark', 'light'):
                        return name
        except Exception:
            pass
    return 'dark'


def _save_theme_name(name: str) -> None:
    try:
        with open(_THEME_STORE, 'w', encoding='utf-8') as f:
            json.dump({'theme': name}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def apply_theme(app: QApplication, name: str = None) -> str:
    """Применяет тему ('dark'|'light') к приложению. Возвращает применённое имя темы."""
    if name is None:
        name = _load_theme_name()
    app.setStyle('Fusion')
    if name == 'light':
        app.setStyleSheet(QSS_LIGHT)
    else:
        name = 'dark'
        app.setStyleSheet(QSS_DARK)
    _save_theme_name(name)
    return name


def apply_windows_dark_titlebar(widget) -> None:
    if platform.system() != "Windows":
        return
    try:
        hwnd = int(widget.winId())
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19
        value = ctypes.c_int(1)
        dwmapi = ctypes.windll.dwmapi
        res = dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value))
        if res != 0:
            dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1, ctypes.byref(value), ctypes.sizeof(value))
    except Exception:
        pass


class ThemedWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._titlebar_dark_applied = False

    def showEvent(self, event):
        super().showEvent(event)
        if not self._titlebar_dark_applied:
            apply_windows_dark_titlebar(self)
            self._titlebar_dark_applied = True


class ThemedDialog(QDialog):
    def showEvent(self, event):
        super().showEvent(event)
        apply_windows_dark_titlebar(self)


