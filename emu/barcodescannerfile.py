"""Распознавание штрихкодов/Datamatrix с изображений через pyrxing."""

from typing import List
import os
import shutil
import tempfile
from .gs1 import normalize_gs1


class BarcodeImageScanner:
    def __init__(self) -> None:
        from pyrxing import read_barcodes  # type: ignore

        self._read_barcodes = read_barcodes

    def _run_pyrxing(self, image_path: str) -> List[str]:
        """Запустить pyrxing для одного файла. Возвращает дедуплицированные, нормализованные строки."""
        results = self._read_barcodes(image_path)

        values: List[str] = []
        for item in results or []:
            parsed = getattr(item, 'text', None)
            if parsed is None and isinstance(item, dict):
                parsed = item.get('text') or item.get('parsed') or item.get('raw') or item.get('data')
            if isinstance(parsed, bytes):
                try:
                    parsed = parsed.decode('utf-8')
                except Exception:
                    parsed = parsed.decode('latin-1', errors='ignore')
            if isinstance(parsed, str) and parsed:
                values.append(normalize_gs1(parsed))

        seen = set()
        uniq: List[str] = []
        for s in values:
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        return uniq

    def decode_image(self, image_path: str) -> List[str]:
        """Возвращает список строк, распознанных из изображения.

        Сначала пытается распознать напрямую. Если не найдено — применяет
        предобработку (контраст, резкость, бинаризация) и повторяет попытку.
        """
        # Копируем во временную директорию, чтобы pyrxing не оставлял артефакты
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, os.path.basename(image_path))
            try:
                shutil.copy2(image_path, tmp_path)
            except Exception:
                tmp_path = image_path  # fallback: используем исходный путь

            values = self._run_pyrxing(tmp_path)
            if values:
                return values

        # Быстрое распознавание не сработало — пробуем предобработку
        try:
            from .image_utils import generate_variants, open_image

            img = open_image(image_path)
            if img is None:
                return []

            variants = generate_variants(img)
            for variant in variants:
                with tempfile.TemporaryDirectory() as _tmpdir:
                    var_path = os.path.join(_tmpdir, "variant.png")
                    variant.save(var_path, 'PNG')
                    values = self._run_pyrxing(var_path)
                    if values:
                        return values
        except ImportError:
            pass  # Pillow не установлен — без предобработки
        except Exception:
            pass

        return []

    def decode_bytes(self, image_bytes: bytes) -> List[str]:
        """Декодировать из байтов изображения в памяти (PNG/JPEG)."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(image_bytes)
            tmp_path = f.name
        try:
            return self.decode_image(tmp_path)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
