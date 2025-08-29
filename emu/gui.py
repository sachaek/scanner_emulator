"""
Модуль графического интерфейса (PyQt)
"""

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from .scanner import BarcodeScanner
from .config import GUI_CONFIG


class ScannerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.scanner = BarcodeScanner()
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        config = GUI_CONFIG

        self.setWindowTitle(config['window_title'])

        # Размер окна из строки вида "400x200"
        try:
            width, height = map(int, str(config.get('window_size', '400x200')).lower().split('x'))
        except Exception:
            width, height = 400, 200
        self.resize(width, height)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        label = QLabel("Введите штрих-код:")
        # Применяем шрифт, если указан
        try:
            font_family, font_size = config['font_style'][0], config['font_style'][1]
            label_font = label.font()
            label_font.setFamily(font_family)
            label_font.setPointSize(int(font_size))
            label.setFont(label_font)
        except Exception:
            pass
        layout.addWidget(label)

        self.entry = QLineEdit()
        try:
            entry_font = self.entry.font()
            entry_font.setFamily(font_family)
            entry_font.setPointSize(int(font_size))
            self.entry.setFont(entry_font)
        except Exception:
            pass
        layout.addWidget(self.entry)

        button = QPushButton("Сканировать")
        # Стили кнопки
        btn_style = config.get('button_style', {})
        bg = btn_style.get('bg')
        fg = btn_style.get('fg')
        if bg or fg:
            button.setStyleSheet(
                f"QPushButton {{"
                f"{'background-color: ' + bg + ';' if bg else ''}"
                f"{'color: ' + fg + ';' if fg else ''}"
                f"}}"
            )
        button.setDefault(True)
        button.clicked.connect(self.on_scan)
        layout.addWidget(button)

        self.entry.returnPressed.connect(self.on_scan)

        self.setLayout(layout)
        self.entry.setFocus()

    def on_scan(self):
        """Обработчик события сканирования"""
        barcode = self.entry.text()

        if not self.scanner.validate_barcode(barcode):
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Длина штрих-кода не может превышать {self.scanner.config['max_length']} символов",
            )
            return

        ret = QMessageBox.information(
            self,
            "Подготовка к сканированию",
            "У вас 2 секунды чтобы переключиться на целевое окно\nНажмите OK для продолжения",
            QMessageBox.Ok
        )
        if ret == QMessageBox.Ok:
            # Запоминаем признак "поверх всех окон"
            was_on_top = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)

            # Убираем "поверх всех" и сворачиваем окно
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self.show()  # нужно переотобразить после смены флага
            self.showMinimized()

            # Эмулируем ввод штрих-кода
            self.scanner.emulate_typing(barcode)

            # Восстанавливаем состояние
            self.setWindowFlag(Qt.WindowStaysOnTopHint, was_on_top)
            self.showNormal()

            # Очищаем поле и возвращаем фокус без навязывания активного окна
            self.entry.clear()
            QTimer.singleShot(100, self.entry.setFocus)