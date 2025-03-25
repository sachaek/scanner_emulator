"""
Конфигурационные параметры приложения
"""

# Настройки эмуляции сканера
SCANNER_CONFIG = {
    'initial_delay': 2.0,  # Задержка перед сканированием (сек)
    'first_char_delay': 0.004,  # Задержка первого символа (сек)
    'char_delay': 0.005,  # Задержка последующих символов (сек)
    'max_length': 30  # Максимальная длина штрих-кода
}

# Настройки GUI
GUI_CONFIG = {
    'window_title': "Сушкоф. Эмулятор сканера штрих-кодов",
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