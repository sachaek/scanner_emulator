"""Пути к пользовательским данным (персистентным настройкам).

В exe (PyInstaller --onefile) запись рядом с модулями невозможна, поэтому
используем директорию профиля пользователя.
"""

import os
import platform


def get_user_data_dir(app_name: str = 'barcode_emulator') -> str:
    system = platform.system()
    base: str
    if system == 'Windows':
        base = os.getenv('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
        path = os.path.join(base, app_name)
    elif system == 'Darwin':
        base = os.path.expanduser('~/Library/Application Support')
        path = os.path.join(base, app_name)
    else:
        base = os.path.expanduser('~/.config')
        path = os.path.join(base, app_name)

    os.makedirs(path, exist_ok=True)
    return path


