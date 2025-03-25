"""
Модуль графического интерфейса
"""

import tkinter as tk
from tkinter import messagebox
from .scanner import BarcodeScanner
from .config import GUI_CONFIG


class ScannerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.scanner = BarcodeScanner()
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        config = GUI_CONFIG

        self.root.title(config['window_title'])
        self.root.geometry(config['window_size'])

        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True, fill=tk.BOTH)

        # Элементы интерфейса
        label = tk.Label(frame, text="Введите штрих-код:", font=config['font_style'])
        label.pack(pady=(0, 10))

        self.entry = tk.Entry(frame, font=config['font_style'], width=30)
        self.entry.pack(pady=(0, 20))

        button = tk.Button(
            frame, text="Сканировать", command=self.on_scan,
            font=config['font_style'], **config['button_style']
        )
        button.pack()

        self.entry.focus_set()
        self.root.bind('<Return>', lambda event: self.on_scan())

    def on_scan(self):
        """Обработчик события сканирования"""
        barcode = self.entry.get()

        if not self.scanner.validate_barcode(barcode):
            messagebox.showerror(
                "Ошибка",
                f"Длина штрих-кода не может превышать {self.scanner.config['max_length']} символов",
                parent=self.root
            )
            return

        messagebox.showinfo(
            "Подготовка к сканированию",
            "У вас 2 секунды чтобы переключиться на целевое окно\nНажмите OK для продолжения",
            parent=self.root
        )

        self.root.withdraw()
        self.scanner.emulate_typing(barcode)
        self.root.destroy()