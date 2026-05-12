"""
Модуль эмуляции сканера штрих-кодов
"""

from pynput.keyboard import Controller, Key, KeyCode
import time
from .config import get_scanner_config
from .gs1 import normalize_gs1, GS


class BarcodeScanner:
    def __init__(self):
        self.keyboard = Controller()
        self.config = get_scanner_config()

    def validate_barcode(self, barcode: str) -> bool:
        """Проверка валидности штрих-кода"""
        self.config = get_scanner_config()
        return len(barcode) <= self.config['max_length']

    # --- Приватные вспомогательные методы ---

    def _press_char(self, char: str) -> None:
        """Нажать и отпустить один символ с настроенными задержками."""
        if char == GS:
            self._press_gs()
        else:
            key_code = KeyCode.from_char(char)
            self.keyboard.press(key_code)
            time.sleep(self.config['key_hold_delay'])
            self.keyboard.release(key_code)
        time.sleep(self.config['char_delay'])

    def _press_gs(self) -> None:
        """Эмулировать GS (0x1D) через Ctrl+].
        Работает в большинстве терминалов и GS1-совместимых приёмников.
        """
        self.keyboard.press(Key.ctrl)
        self.keyboard.press(KeyCode.from_char(']'))
        time.sleep(self.config['key_hold_delay'])
        self.keyboard.release(KeyCode.from_char(']'))
        self.keyboard.release(Key.ctrl)

    def _press_enter(self) -> None:
        """Нажать и отпустить Enter."""
        self.keyboard.press(Key.enter)
        time.sleep(self.config['key_hold_delay'])
        self.keyboard.release(Key.enter)

    def _type_string(self, text: str, append_enter: bool = True) -> None:
        """Напечатать строку посимвольно с опциональным завершающим Enter."""
        for char in text:
            self._press_char(char)
        if append_enter:
            self._press_enter()

    # --- Публичные методы ---

    def emulate_typing(self, barcode: str) -> None:
        """Эмуляция ввода одного штрих-кода с завершающим Enter."""
        self.config = get_scanner_config()
        time.sleep(self.config['initial_delay'])
        if self.config['first_char_delay']:
            time.sleep(self.config['first_char_delay'])

        payload = normalize_gs1(barcode)
        self._type_string(payload, append_enter=True)

    def emulate_batch_typing(self, barcodes: list[str]) -> None:
        """Эмуляция ввода нескольких штрих-кодов подряд.
        Задержка перед сканированием выполняется один раз.
        Коды длиннее max_length пропускаются (не обрезаются).
        """
        if not barcodes:
            return
        self.config = get_scanner_config()
        time.sleep(self.config['initial_delay'])
        if self.config['first_char_delay']:
            time.sleep(self.config['first_char_delay'])

        max_len = self.config['max_length']
        for code in barcodes:
            if not isinstance(code, str):
                continue
            if len(code) > max_len:
                continue  # Пропускаем, а не обрезаем молча
            payload = normalize_gs1(code)
            self._type_string(payload, append_enter=True)
            time.sleep(self.config['inter_code_delay'])