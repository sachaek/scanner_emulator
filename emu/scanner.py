"""
Модуль эмуляции сканера штрих-кодов
"""

from pynput.keyboard import Controller, Key
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

        for i, char in enumerate(barcode):
            self.keyboard.press(char)
            self.keyboard.release(char)
            delay = self.config['first_char_delay'] if i == 0 else self.config['char_delay']
            time.sleep(delay)

        self.keyboard.press(Key.enter)
        self.keyboard.release(Key.enter)
        # Убрали завершение программы