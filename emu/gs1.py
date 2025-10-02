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


AI_FIXED_LENGTH: Dict[str, int] = {
    # Наиболее распространённые фиксированные AI (неполный список)
    "00": 18,  # SSCC
    "01": 14,  # GTIN
    "02": 14,  # GTIN контейнера/содержимого
    "11": 6,   # Дата производства YYMMDD
    "12": 6,   # Дата срок эксплуатации
    "13": 6,   # Дата упаковки
    "15": 6,   # Годен до
    "17": 6,   # Срок годности
    "20": 2,   # Кол-во единиц в потребительской упаковке
    # Ещё десятки AI фикcированной длины опущены для краткости
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


