"""
Модуль графического интерфейса (PyQt)
"""

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QAction
from .scanner import BarcodeScanner
from .config import GUI_CONFIG
from .theme import ThemedWindow


class ScannerGUI(ThemedWindow):
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

        # Центральный виджет и layout
        central = QWidget(self)
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
        # Темing управляется глобальным QSS в QApplication
        button.setDefault(True)
        button.clicked.connect(self.on_scan)
        layout.addWidget(button)

        self.entry.returnPressed.connect(self.on_scan)

        central.setLayout(layout)
        self.setCentralWidget(central)
        self._build_menu()
        self.entry.setFocus()

    def showEvent(self, event):
        super().showEvent(event)

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


    def open_scan_params(self):
        from .pages.scan_params import ScanParamsDialog
        dlg = ScanParamsDialog(self)
        dlg.exec_()

    def _build_menu(self) -> None:
        menubar = self.menuBar()

        menu_file = menubar.addMenu("Файл")
        act_exit = QAction("Выход", self)
        act_exit.triggered.connect(self.close)
        menu_file.addAction(act_exit)

        menu_params = menubar.addMenu("Параметры")
        act_scan_params = QAction("Параметры сканирования", self)
        act_scan_params.triggered.connect(self.open_scan_params)
        menu_params.addAction(act_scan_params)