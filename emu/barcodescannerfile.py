"""Распознавание штрихкодов/Datamatrix с изображений через pyzxing."""

from typing import List


class BarcodeImageScanner:
    def __init__(self) -> None:
        # Импортируем здесь, чтобы не падать при старте, если зависимость не установлена
        from pyzxing import BarCodeReader  # type: ignore

        self.reader = BarCodeReader()

    def decode_image(self, image_path: str) -> List[str]:
        """Возвращает список строк, распознанных из изображения."""
        results = self.reader.decode(image_path)
        values: List[str] = []
        for item in results or []:
            parsed = item.get('parsed') if isinstance(item, dict) else None
            if isinstance(parsed, bytes):
                try:
                    parsed = parsed.decode('utf-8')
                except Exception:
                    parsed = parsed.decode('latin-1', errors='ignore')
            if isinstance(parsed, str) and parsed:
                values.append(parsed)

        # Удаляем дубликаты, сохраняя порядок
        seen = set()
        uniq: List[str] = []
        for s in values:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        return uniq


