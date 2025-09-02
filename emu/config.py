"""
Конфигурационные параметры приложения
"""

import json
import os
from typing import Dict, Any
from .paths import get_user_data_dir


# Настройки эмуляции сканера (умолчания)
SCANNER_CONFIG_DEFAULT: Dict[str, Any] = {
    'initial_delay': 2.0,  # Задержка перед сканированием (сек)
    'first_char_delay': 0.0,  # Задержка первого символа (сек)
    'char_delay': 0.005,  # Задержка последующих символов (сек)
    'key_hold_delay': 0.005,  # Удержание клавиши перед отпусканием (сек)
    'max_length': 55  # Максимальная длина штрих-кода
}

_OVERRIDE_PATH = os.path.join(get_user_data_dir(), 'scanner_config.json')

# Миграция старого расположения (рядом с модулем) -> в профиль пользователя
_OLD_OVERRIDE_PATH = os.path.join(os.path.dirname(__file__), 'scanner_config.json')
if os.path.exists(_OLD_OVERRIDE_PATH) and not os.path.exists(_OVERRIDE_PATH):
    try:
        os.replace(_OLD_OVERRIDE_PATH, _OVERRIDE_PATH)
    except Exception:
        pass


def _load_override() -> Dict[str, Any]:
    if not os.path.exists(_OVERRIDE_PATH):
        return {}
    try:
        with open(_OVERRIDE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def get_scanner_config() -> Dict[str, Any]:
    """Возвращает текущую конфигурацию: умолчания + оверрайд из файла."""
    cfg = dict(SCANNER_CONFIG_DEFAULT)
    override = _load_override()
    for k, v in override.items():
        if k in cfg:
            cfg[k] = v
    return cfg


def save_scanner_override(new_values: Dict[str, Any]) -> None:
    """Сохраняет только переопределённые значения в JSON."""
    cleaned: Dict[str, Any] = {}
    for k, v in new_values.items():
        if k in SCANNER_CONFIG_DEFAULT and SCANNER_CONFIG_DEFAULT[k] != v:
            cleaned[k] = v
    if cleaned:
        with open(_OVERRIDE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
    else:
        # если отличий нет — удаляем файл оверрайда
        if os.path.exists(_OVERRIDE_PATH):
            os.remove(_OVERRIDE_PATH)


def reset_scanner_override() -> None:
    """Удаляет файл оверрайда, восстанавливая умолчания."""
    if os.path.exists(_OVERRIDE_PATH):
        os.remove(_OVERRIDE_PATH)


# Настройки GUI
GUI_CONFIG = {
    'window_title': "Scanner emu",
    'window_size': "400x200",
    'font_style': ("Arial", 12),
    'button_style': {
        'bg': "#4CAF50",
        'fg': "white",
        'height': 1,
        'width': 15,
    },
    'rescan_delay': 0.5
}