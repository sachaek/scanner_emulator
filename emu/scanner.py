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
        # Всегда читаем актуальную конфигурацию (учитывает изменения в UI)
        self.config = get_scanner_config()
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

        # Нормализуем GS1-строку: скобки -> GS-разделители
        payload = normalize_gs1(barcode)

        for i, char in enumerate(payload):
            # Ctrl+] используется как способ ввести GS (0x1D) во многие приёмники
            if char == GS:
                # Попытка «вбить» ASCII 29 как Ctrl+]
                self.keyboard.press(Key.ctrl)
                self.keyboard.press(KeyCode.from_char(']'))
                time.sleep(self.config.get('key_hold_delay', 0.0))
                self.keyboard.release(KeyCode.from_char(']'))
                self.keyboard.release(Key.ctrl)
                time.sleep(self.config.get('char_delay', 0.0))
                continue

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
            payload = normalize_gs1(code)
            for ch in payload:
                if ch == GS:
                    self.keyboard.press(Key.ctrl)
                    self.keyboard.press(KeyCode.from_char(']'))
                    time.sleep(self.config.get('key_hold_delay', 0.0))
                    self.keyboard.release(KeyCode.from_char(']'))
                    self.keyboard.release(Key.ctrl)
                    time.sleep(self.config.get('char_delay', 0.0))
                    continue
                key_code = KeyCode.from_char(ch)
                self.keyboard.press(key_code)
                time.sleep(self.config.get('key_hold_delay', 0.0))
                self.keyboard.release(key_code)
                time.sleep(self.config.get('char_delay', 0.0))
            # Enter после каждого кода
            self.keyboard.press(Key.enter)
            time.sleep(self.config.get('key_hold_delay', 0.0))
            self.keyboard.release(Key.enter)