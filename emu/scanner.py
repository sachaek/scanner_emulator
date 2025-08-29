"""
Модуль эмуляции сканера штрих-кодов
"""

from pynput.keyboard import Controller, Key, KeyCode
import time
from .config import get_scanner_config


class BarcodeScanner:
    def __init__(self):
        self.keyboard = Controller()
        self.config = get_scanner_config()

    def validate_barcode(self, barcode: str) -> bool:
        """Проверка валидности штрих-кода"""
        return len(barcode) <= self.config['max_length']

    def emulate_typing(self, barcode: str) -> None:
        """
        Эмуляция ввода штрих-кода
        :param barcode: Строка штрих-кода
        :return: None
        """
        # Обновляем конфиг на случай, если он был изменён пользователем
        self.config = get_scanner_config()
        time.sleep(self.config['initial_delay'])

        # Доп. пауза перед самым первым символом, чтобы целевое окно гарантированно приняло фокус
        time.sleep(self.config.get('first_char_delay', 0.0))

        for i, char in enumerate(barcode):
            key_code = KeyCode.from_char(char)
            self.keyboard.press(key_code)
            time.sleep(self.config.get('key_hold_delay', 0.0))
            self.keyboard.release(key_code)
            time.sleep(self.config.get('char_delay', 0.0))

        # Завершаем Enter с теми же паузами
        self.keyboard.press(Key.enter)
        time.sleep(self.config.get('key_hold_delay', 0.0))
        self.keyboard.release(Key.enter)
        # Убрали завершение программы

    def emulate_batch_typing(self, barcodes: list[str]) -> None:
        """Эмуляция ввода нескольких штрих-кодов подряд. Задержка перед сканированием выполняется один раз."""
        if not barcodes:
            return
        # Обновляем конфиг
        self.config = get_scanner_config()
        time.sleep(self.config['initial_delay'])
        time.sleep(self.config.get('first_char_delay', 0.0))

        for idx, code in enumerate(barcodes):
            if not isinstance(code, str):
                continue
            # Обрезаем по максимальной длине из конфига
            if len(code) > self.config.get('max_length', 30):
                code = code[: self.config.get('max_length', 30)]
            for ch in code:
                key_code = KeyCode.from_char(ch)
                self.keyboard.press(key_code)
                time.sleep(self.config.get('key_hold_delay', 0.0))
                self.keyboard.release(key_code)
                time.sleep(self.config.get('char_delay', 0.0))
            # Enter после каждого кода
            self.keyboard.press(Key.enter)
            time.sleep(self.config.get('key_hold_delay', 0.0))
            self.keyboard.release(Key.enter)