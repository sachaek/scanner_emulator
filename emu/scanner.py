"""
Модуль эмуляции сканера штрих-кодов
"""

from pynput.keyboard import Controller, Key, KeyCode
import time
from .config import SCANNER_CONFIG


class BarcodeScanner:
    def __init__(self):
        self.keyboard = Controller()
        self.config = SCANNER_CONFIG

    def validate_barcode(self, barcode: str) -> bool:
        """Проверка валидности штрих-кода"""
        return len(barcode) <= self.config['max_length']

    def emulate_typing(self, barcode: str) -> None:
        """
        Эмуляция ввода штрих-кода
        :param barcode: Строка штрих-кода
        :return: None
        """
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