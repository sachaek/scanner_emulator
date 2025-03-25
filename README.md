# Эмулятор сканера штрих-кодов

Программа для эмуляции ввода штрих-кодов с клавиатуры. Позволяет вводить штрих-коды в любое приложение, как если бы использовался физический сканер.

## Особенности

- Кроссплатформенная работа (Windows, Linux, macOS)
- Реалистичная эмуляция ввода с настраиваемыми задержками
- Portable версии для всех платформ
- Не перехватывает фокус после сканирования

## Установка

### Windows
1. Скачайте `barcode_emulator.exe` из папки `dist_windows`
2. Запустите исполняемый файл

### Linux
```bash
# Требуется python3 и xdotool
sudo apt-get install python3 python3-pip xdotool
pip3 install pynput
python3 -m barcode_emulator.main
```

### macOS
```bash
brew install python
pip3 install pynput
python3 -m barcode_emulator.main
```

## Сборка исполняемых файлов

### Для Windows
```bash
pyinstaller --onefile --windowed --icon=app.ico emu/main.py -n barcode_emulator
```
Сборка появится в `dist_windows/`

### Для Linux (используя PyInstaller)
```bash
pyinstaller --onefile emu/main.py -n barcode_emulator_linux
```
Требуемые зависимости:
```bash
sudo apt-get install python3-dev libx11-dev
```

### Для macOS
```bash
pyinstaller --onefile --windowed emu/main.py -n barcode_emulator_mac
```

## Структура проекта

```
barcode_emulator/
├── dist_windows/          # Windows сборки
├── dist_linux/            # Linux сборки
├── dist_mac/              # macOS сборки
├── emu/                   # Исходный код
│   ├── __init__.py
│   ├── main.py
│   ├── scanner.py
│   ├── gui.py
│   └── config.py
├── app.ico                # Иконка для Windows
└── requirements.txt       # Зависимости
```

## Особенности для разных ОС

### Linux
- Требуется установленный `xdotool` для управления окнами
- Может потребоваться запуск с правами sudo
- Для работы в Wayland потребуется дополнительная настройка

### macOS
- Необходимо разрешить программе управление вводом:
  ```bash
  python3 -m pip install pyobjc
  ```
- В настройках безопасности разрешите управление компьютером

## Настройки

Редактируйте `emu/config.py`:

```python
SCANNER_CONFIG = {
    'initial_delay': 2.0,      # Задержка перед сканированием
    'first_char_delay': 0.004, 
    'char_delay': 0.005,
    'max_length': 30,
    'os_specific_delay': 0.1   # Доп. задержка для Linux/macOS
}
```

---

> **Важно:** На Linux/macOS программа может требовать дополнительных разрешений для эмуляции ввода.