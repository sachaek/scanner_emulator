"""Распознавание штрихкодов/Datamatrix с изображений через pyrxing."""

from typing import List
from .gs1 import normalize_gs1


class BarcodeImageScanner:
    def __init__(self) -> None:
        # Ленивый импорт, чтобы приложение запускалось без установленной зависимости
        # Функция сохраняется как атрибут экземпляра
        from pyrxing import read_barcodes  # type: ignore

        self._read_barcodes = read_barcodes

    def decode_image(self, image_path: str) -> List[str]:
        """Возвращает список строк, распознанных из изображения."""
        results = self._read_barcodes(image_path)
        values: List[str] = []
        for item in results or []:
            # pyrxing обычно возвращает объекты с атрибутом .text
            parsed = getattr(item, 'text', None)
            # На всякий случай поддержим словари или иные поля
            if parsed is None and isinstance(item, dict):
                parsed = item.get('text') or item.get('parsed') or item.get('raw') or item.get('data')
            if isinstance(parsed, bytes):
                try:
                    parsed = parsed.decode('utf-8')
                except Exception:
                    parsed = parsed.decode('latin-1', errors='ignore')
            if isinstance(parsed, str) and parsed:
                # Нормализуем к стандартному виду GS1 (убираем скобки, добавляем GS между переменной длиной)
                values.append(normalize_gs1(parsed))

        # Удаляем дубликаты, сохраняя порядок
        seen = set()
        uniq: List[str] = []
        for s in values:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        return uniq


