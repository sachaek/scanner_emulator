"""Захват ввода физического HID сканера с таймингами и спецсимволами."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional

from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from .paths import get_user_data_dir

_SPECIAL_KEYS = {
    Key.tab: "TAB",
    Key.space: "SPACE",
    Key.esc: "ESC",
    Key.backspace: "BACKSPACE",
    Key.delete: "DELETE",
    Key.shift: "SHIFT",
    Key.shift_r: "SHIFT_R",
    Key.ctrl: "CTRL",
    Key.ctrl_r: "CTRL_R",
    Key.alt: "ALT",
    Key.alt_r: "ALT_R",
    Key.caps_lock: "CAPS_LOCK",
    Key.f1: "F1", Key.f2: "F2", Key.f3: "F3", Key.f4: "F4",
    Key.f5: "F5", Key.f6: "F6", Key.f7: "F7", Key.f8: "F8",
    Key.f9: "F9", Key.f10: "F10", Key.f11: "F11", Key.f12: "F12",
    Key.home: "HOME", Key.end: "END",
    Key.page_up: "PG_UP", Key.page_down: "PG_DN",
    Key.insert: "INSERT",
    Key.up: "UP", Key.down: "DOWN", Key.left: "LEFT", Key.right: "RIGHT",
    Key.menu: "MENU",
    Key.pause: "PAUSE",
    Key.print_screen: "PRT_SC",
}


@dataclass
class ScanCapture:
    """Один захваченный скан: содержимое, посимвольная расшифровка, метрики."""
    timestamp: float = 0.0
    barcode: str = ""
    chars: list = field(default_factory=list)
    total_duration_ms: float = 0.0
    avg_interchar_delay_ms: float = 0.0

    @property
    def special_keys(self) -> list[str]:
        return [c["char"] for c in self.chars if c.get("is_special")]

    def to_dict(self) -> dict:
        return {
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "barcode": self.barcode,
            "chars": self.chars,
            "special_keys": self.special_keys,
            "total_duration_ms": self.total_duration_ms,
            "char_count": len(self.chars),
            "avg_interchar_delay_ms": self.avg_interchar_delay_ms,
        }


class ScannerCapture:
    """Захватывает ввод физического HID сканера через pynput.keyboard.Listener.

    - Фильтрует собственные эмитированные события (injected)
    - Накапливает символы с задержками (time.perf_counter)
    - По ENTER завершает скан, логирует и оповещает через callback
    """

    def __init__(self, on_capture: Optional[Callable] = None):
        self._on_capture = on_capture
        self._listener: Optional[keyboard.Listener] = None
        self._buffer: list[dict] = []
        self._last_perf: Optional[float] = None
        self._scan_start_wall: Optional[float] = None
        self._captures: list[ScanCapture] = []
        self._suppress = False

    # --- Публичные методы ---

    @property
    def is_running(self) -> bool:
        return self._listener is not None and self._listener.running

    @property
    def captures(self) -> list[ScanCapture]:
        return list(self._captures)

    def start(self, suppress: bool = False) -> None:
        """Запустить захват (глобальный keyboard hook)."""
        if self.is_running:
            return
        self._suppress = suppress
        self._buffer.clear()
        self._last_perf = None
        self._scan_start_wall = None
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            suppress=suppress,
        )
        self._listener.start()

    def stop(self) -> None:
        """Остановить захват и освободить hook."""
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._buffer.clear()
        self._last_perf = None
        self._scan_start_wall = None

    # --- Внутренняя логика ---

    def _on_press(self, key, injected: bool = False):
        """Callback pynput — вызывается из фонового потока."""
        if injected:
            return True  # не подавлять свои же события

        now_perf = time.perf_counter()

        # Задержка от предыдущего события
        delay_ms = 0.0
        if self._last_perf is not None:
            delay_ms = (now_perf - self._last_perf) * 1000
        self._last_perf = now_perf

        # Запоминаем wall‑clock первого нажатия (для таймстемпа скана)
        if not self._buffer:
            self._scan_start_wall = time.time()

        # ENTER — завершаем текущий скан
        if key == Key.enter:
            self._finalize_scan(delay_ms)
            return not self._suppress

        # Спецклавиша
        name = _SPECIAL_KEYS.get(key)
        if name is not None:
            self._buffer.append({
                "char": f"[{name}]",
                "delay_ms": round(delay_ms, 1),
                "is_special": True,
            })
            return not self._suppress

        # Неизвестная спецклавиша (Key без char и не в словаре)
        if isinstance(key, Key):
            self._buffer.append({
                "char": f"[VK_{key.value.vk}]",
                "delay_ms": round(delay_ms, 1),
                "is_special": True,
            })
            return not self._suppress

        # Обычный символ
        if hasattr(key, 'char') and key.char is not None:
            self._buffer.append({
                "char": key.char,
                "delay_ms": round(delay_ms, 1),
                "is_special": False,
            })
            return not self._suppress

        return not self._suppress

    def _finalize_scan(self, enter_delay_ms: float) -> None:
        """Завершить текущий скан, сформировать ScanCapture, сохранить, оповестить."""
        if not self._buffer:
            return

        # Добавляем ENTER как последнее событие
        self._buffer.append({
            "char": "[ENTER]",
            "delay_ms": enter_delay_ms,
            "is_special": True,
        })

        # Собираем barcode из обычных символов (без спецклавиш)
        barcode_chars = [
            c["char"] for c in self._buffer
            if not c.get("is_special")
        ]
        barcode = "".join(barcode_chars)

        # Метрики
        delays = [c["delay_ms"] for c in self._buffer[1:]]
        total_duration = round(sum(delays), 1) if delays else 0.0

        non_special_delays = [
            c["delay_ms"] for c in self._buffer[1:]
            if not c.get("is_special")
        ]
        avg_delay = (
            round(sum(non_special_delays) / len(non_special_delays), 1)
            if non_special_delays
            else 0.0
        )

        capture = ScanCapture(
            timestamp=self._scan_start_wall or time.time(),
            barcode=barcode,
            chars=list(self._buffer),
            total_duration_ms=total_duration,
            avg_interchar_delay_ms=avg_delay,
        )

        self._captures.append(capture)
        self._save_capture(capture)

        if self._on_capture:
            self._on_capture(capture)

        self._buffer.clear()
        self._last_perf = None
        self._scan_start_wall = None

    # --- Логирование ---

    def _save_capture(self, capture: ScanCapture) -> None:
        log_dir = os.path.join(get_user_data_dir(), "debug_logs")
        os.makedirs(log_dir, exist_ok=True)
        self._append_jsonl(os.path.join(log_dir, "captures.jsonl"), capture)
        self._append_text_log(os.path.join(log_dir, "captures.log"), capture)

    @staticmethod
    def _append_jsonl(path: str, capture: ScanCapture) -> None:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(capture.to_dict(), ensure_ascii=False) + "\n")

    @staticmethod
    def _append_text_log(path: str, capture: ScanCapture) -> None:
        lines = [
            f"=== Scan Capture: {datetime.fromtimestamp(capture.timestamp).isoformat()} ===",
            f"Barcode: {capture.barcode}",
            f"Char count: {len(capture.chars)} | Duration: {capture.total_duration_ms}ms"
            f" | Avg delay: {capture.avg_interchar_delay_ms}ms",
            "",
            "Character breakdown:",
            " # | Char       | Delay(ms) | Notes",
            "---|------------|-----------|----------------",
        ]
        for i, c in enumerate(capture.chars):
            note = ""
            if i == 0:
                note = "first char"
            elif c.get("char") == "[ENTER]":
                note = "suffix"
            c_char = c.get("char", "?")
            if len(c_char) > 10:
                c_char = c_char[:9] + "…"
            lines.append(
                f"{i:>2} | {c_char:<10} | {c['delay_ms']:>7.1f}  | {note}"
            )

        lines.extend([
            "",
            f"Special keys: {', '.join(capture.special_keys) or 'none'}",
            "=" * 52,
            "",
        ])
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def format_capture_detail(self, capture: ScanCapture) -> str:
        """Форматирует детальную расшифровку захвата для отображения в UI."""
        lines = [
            f"Barcode: {capture.barcode}",
            f"Chars: {len(capture.chars)}  |  "
            f"Duration: {capture.total_duration_ms}ms  |  "
            f"Avg delay: {capture.avg_interchar_delay_ms}ms",
            "",
            "Character breakdown:",
            "  # | Char       | Delay(ms) | Notes",
            "  --|------------|-----------|----------------",
        ]
        for i, c in enumerate(capture.chars):
            note = ""
            if i == 0:
                note = "first char"
            elif c.get("char") == "[ENTER]":
                note = "suffix"
            c_char = c.get("char", "?")
            if len(c_char) > 10:
                c_char = c_char[:9] + "…"
            lines.append(
                f"  {i:>2} | {c_char:<10} | {c['delay_ms']:>7.1f} | {note}"
            )

        special = capture.special_keys
        if special:
            lines.append(f"\nSpecial keys: {', '.join(special)}")

        lines.append(f"\nTimestamp: {datetime.fromtimestamp(capture.timestamp)}")
        return "\n".join(lines)
