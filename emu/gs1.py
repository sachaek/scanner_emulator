"""Утилиты для нормализации строк GS1/AI.

Цель: преобразовывать человеко‑читаемые строки вида
"(01)04602433001966(21)5!y<jl(93)eAMR" в формат передачи без скобок
с разделителем GS (ASCII 0x1D) после переменной длины, например:
"0104602433001966215!y<jl\x1D93eAMR".

Если вход уже в «передаваемом» формате (без скобок), возвращается как есть.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


# AI измерений (3100-3699): NET WEIGHT (kg), LENGTH (m), VOLUME (l), и т.д.
# Формат: 3XXd, где XX=10..69, d=0..9 (позиция десятичной точки)
_MEASURE_AI: Dict[str, int] = {f"{i}{j}": 6 for i in range(310, 370) for j in range(10)}

AI_FIXED_LENGTH: Dict[str, int] = {
    **_MEASURE_AI,

    # 2-значные AI
    "00": 18,    # SSCC
    "01": 14,    # GTIN
    "02": 14,    # GTIN содержимого
    "11": 6,     # Дата производства (YYMMDD)
    "12": 6,     # Срок эксплуатации (YYMMDD)
    "13": 6,     # Дата упаковки (YYMMDD)
    "15": 6,     # Годен до (YYMMDD)
    "17": 6,     # Срок годности (YYMMDD)
    "20": 2,     # Вариант продукта

    # 3-значные AI
    "3370": 6,   # кг / м²
    "3371": 6,   # кг / м² (1 десятичный знак)
    "3372": 6,   # кг / м² (2 десятичных знака)
    "3373": 6,   # кг / м² (3 десятичных знака)
    "3374": 6,   # кг / м² (4 десятичных знака)
    "3375": 6,   # кг / м² (5 десятичных знаков)
    "3376": 6,   # кг / м² (6 десятичных знаков)
    "3377": 6,   # кг / м² (7 десятичных знаков)
    "3378": 6,   # кг / м² (8 десятичных знаков)
    "3379": 6,   # кг / м² (9 десятичных знаков)
    "402": 17,   # GDTI (Global Document Type Identifier)
    "410": 13,   # GLN — отгрузить/доставить
    "411": 13,   # GLN — выставить счёт
    "412": 13,   # GLN — приобретено у
    "413": 13,   # GLN — отгрузить для
    "414": 13,   # GLN физического местоположения
    "415": 13,   # GLN стороны-плательщика
    "416": 13,   # GLN места производства/услуги
    "417": 13,   # GLN стороны

    # 4-значные AI
    "422": 3,    # Страна происхождения товара (ISO 3166-1)
    "424": 3,    # Страна переработки (ISO 3166-1)
    "425": 3,    # Страна демонтажа (ISO 3166-1)
    "426": 3,    # Страна полной переработки (ISO 3166-1)
    "7003": 6,   # Дата/время истечения срока (YYMMDDHHMM)
    "7006": 6,   # Дата первой заморозки (YYMMDD)
    "7007": 6,   # Дата сбора урожая (YYMMDD)
    "7010": 1,   # Метод производства
    "8001": 14,  # Размеры (ширина х длина х глубина х диаметр х площадь)
    "8003": 14,  # GRAI (Global Returnable Asset Identifier)
    "8005": 6,   # Цена за единицу
    "8006": 18,  # GITIN (Global Individual Trade Item Identifier)
    "8008": 12,  # Дата/время производства (YYMMDDHHMMSS)
    "8017": 18,  # GSRN — поставщик (Global Service Relation Number)
    "8018": 18,  # GSRN — получатель
    "8019": 10,  # SRIN (Service Relation Instance Number)
    "8026": 18,  # ITIP (Individual Trade Item Piece)
    "8100": 1,   # Расширенный код купона (сетевая цена)
    "8101": 1,   # Расширенный код купона (альтернативная цена)
    "8102": 1,   # Расширенный код купона (верхняя граница)
}


GS = "\x1D"


_AI_PATTERN = re.compile(r"\((\d{2,4})\)")


def _parse_parenthesized(text: str) -> List[Tuple[str, str]]:
    """Парсит строку вида "(01)....(21)....(93)...." -> список (AI, DATA).

    Значение каждого AI берётся как подстрока между этим AI и следующим AI
    (или концом строки).
    """
    pairs: List[Tuple[str, str]] = []
    matches = list(_AI_PATTERN.finditer(text))
    if not matches:
        return []

    for idx, m in enumerate(matches):
        ai = m.group(1)
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        value = text[start:end]
        pairs.append((ai, value))
    return pairs


def normalize_gs1(text: str) -> str:
    """Нормализует строку GS1 к «стандартному» виду для передачи:
    - Без скобок вокруг AI
    - Между элементами после переменной длины вставляется GS (0x1D)

    Если строка уже без скобок или содержит GS, возвращается как есть.
    """
    if not text:
        return text

    # Если уже содержит GS или похожа на «сырой» вид (нет скобок) — не трогаем
    if GS in text or "(" not in text:
        return text

    pairs = _parse_parenthesized(text)
    if not pairs:
        return text

    out_parts: List[str] = []
    for i, (ai, value) in enumerate(pairs):
        out_parts.append(ai)
        out_parts.append(value)

        is_last = (i == len(pairs) - 1)
        is_fixed = ai in AI_FIXED_LENGTH

        # Для переменной длины и если не последний элемент — добавляем GS
        if (not is_fixed) and (not is_last):
            out_parts.append(GS)

    return "".join(out_parts)


__all__ = ["normalize_gs1", "GS"]


