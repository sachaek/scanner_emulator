"""Настройки стиля: выбор темы (тёмная/светлая)."""

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QComboBox, QDialogButtonBox
from ..theme import ThemedDialog, apply_theme, apply_windows_dark_titlebar
from PyQt5.QtWidgets import QApplication


class StyleSettingsDialog(ThemedDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки — Стиль")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Тема оформления:"))
        self.cb_theme = QComboBox()
        self.cb_theme.addItem("Тёмная", userData='dark')
        self.cb_theme.addItem("Светлая", userData='light')
        layout.addWidget(self.cb_theme)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def on_accept(self):
        name = self.cb_theme.currentData()
        app = QApplication.instance()
        if app is not None:
            applied = apply_theme(app, name)
            # Переключаем тёмный заголовок только если тема тёмная
            if applied == 'dark':
                apply_windows_dark_titlebar(self.parent() or self)
            self.accept()


