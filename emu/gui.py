"""
Модуль графического интерфейса (PyQt)
"""

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QAction, QFileDialog
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

        img_btn = QPushButton("Сканировать изображение…")
        img_btn.clicked.connect(self.on_scan_image)
        layout.addWidget(img_btn)

        from_file_btn = QPushButton("Сканировать из файла…")
        from_file_btn.clicked.connect(self.on_scan_from_file)
        layout.addWidget(from_file_btn)

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

    def on_scan_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл со штрих-кодами", "", "Text Files (*.txt);;All Files (*)")
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать файл:\n{e}")
            return

        if not lines:
            QMessageBox.information(self, "Пусто", "Файл не содержит штрих-кодов")
            return

        ret = QMessageBox.information(
            self,
            "Подготовка к сканированию",
            "У вас 2 секунды чтобы переключиться на целевое окно\nНажмите OK для начала пакетного сканирования",
            QMessageBox.Ok
        )
        if ret != QMessageBox.Ok:
            return

        was_on_top = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.show()
        self.showMinimized()

        self.scanner.emulate_batch_typing(lines)

        self.setWindowFlag(Qt.WindowStaysOnTopHint, was_on_top)
        self.showNormal()

    def on_scan_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)")
        if not path:
            return
        try:
            from .barcodescannerfile import BarcodeImageScanner
            reader = BarcodeImageScanner()
            values = reader.decode_image(path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось распознать изображение:\n{e}")
            return

        if not values:
            QMessageBox.information(self, "Результат", "Коды не найдены")
            return

        # Подставляем первый найденный код в поле ввода и ставим фокус
        self.entry.setText(values[0])
        self.entry.setFocus()
        self.entry.selectAll()


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

        menu_settings = menubar.addMenu("Настройки")
        act_style = QAction("Стиль", self)
        act_style.triggered.connect(self.open_style_settings)
        menu_settings.addAction(act_style)

    def open_style_settings(self):
        from .pages.settings_style import StyleSettingsDialog
        dlg = StyleSettingsDialog(self)
        dlg.exec_()