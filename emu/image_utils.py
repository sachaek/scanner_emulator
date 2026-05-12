"""
Предобработка изображений для улучшения распознавания штрих-кодов.

Позволяет сгенерировать несколько вариантов одного изображения
(контраст, резкость, бинаризация) для последовательных попыток распознавания.
"""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image as PILImage


def _get_pil():
    """Ленивый импорт PIL.Image. Возвращает None, если Pillow не установлен."""
    try:
        from PIL import Image as PILImage
        return PILImage
    except ImportError:
        return None


def _require_pil():
    pil = _get_pil()
    if pil is None:
        raise ImportError("Pillow не установлен. Установите: pip install Pillow")
    return pil


def to_grayscale(image: PILImage.Image) -> PILImage.Image:
    """Преобразовать изображение в оттенки серого."""
    return image.convert('L')


def enhance_contrast(image: PILImage.Image) -> PILImage.Image:
    """Повысить контраст через автоконтраст (отсечка 5% по краям гистограммы)."""
    from PIL import ImageOps
    return ImageOps.autocontrast(image, cutoff=5)


def sharpen(image: PILImage.Image, factor: float = 2.0) -> PILImage.Image:
    """Применить повышение резкости."""
    from PIL import ImageEnhance
    return ImageEnhance.Sharpness(image).enhance(factor)


def binarize(image: PILImage.Image, threshold: int = 128) -> PILImage.Image:
    """Бинаризовать изображение (чёрно-белое, пороговое преобразование)."""
    return image.point(lambda x: 255 if x > threshold else 0, mode='1').convert('L')


def upscale(image: PILImage.Image, factor: float = 2.0) -> PILImage.Image:
    """Увеличить изображение (полезно для маленьких кодов)."""
    new_size = (int(image.width * factor), int(image.height * factor))
    return image.resize(new_size, _get_pil().LANCZOS)


def generate_variants(image: PILImage.Image) -> List[PILImage.Image]:
    """Сгенерировать варианты предобработки для последовательных попыток.

    Порядок: от наименее агрессивной обработки к наиболее агрессивной.
    """
    gray = to_grayscale(image)

    return [
        gray,                                      # 1. Простое灰度
        enhance_contrast(gray),                     # 2. Контраст
        sharpen(gray),                              # 3. Резкость
        sharpen(enhance_contrast(gray)),             # 4. Контраст + резкость
        binarize(gray),                             # 5. Бинаризация
    ]


def open_image(path: str) -> Optional[PILImage.Image]:
    """Открыть изображение по пути. Возвращает None при ошибке."""
    try:
        pil = _require_pil()
        return pil.open(path)
    except Exception:
        return None
