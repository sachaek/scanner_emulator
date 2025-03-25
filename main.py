from tkinter import messagebox

from pynput.keyboard import Controller, Key
import tkinter as tk
import time


def scan_barcode():
    barcode = entry.get()
    if len(barcode) > 30:
        label.config(text="Длина строки не может быть больше 30")
        return

    response = messagebox.showinfo(
        "Подготовка к сканированию",
        "У вас 2 секунды чтобы переключиться на целевое окно для сканирования штрих-кода\n"
        "Нажмите OK для продолжения",
        parent=root
    )

    root.withdraw()  # Скрываем окно
    time.sleep(2)  # Даём время свернуть GUI

    keyboard = Controller()
    delays_ms = [4] + [5] * (len(barcode) - 1)

    for i, char in enumerate(barcode):
        keyboard.press(char)
        keyboard.release(char)
        if i < len(delays_ms):
            time.sleep(delays_ms[i] / 1000)

    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    root.destroy()  # Закрываем программу


# Создаем главное окно
root = tk.Tk()
root.title("Сушкоф. Эмулятор сканера штрих-кодов")
root.geometry("400x200")  # Устанавливаем размер окна 400x200 пикселей

# Настраиваем шрифт
font_style = ("Arial", 12)

# Создаем рамку для группировки элементов
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True, fill=tk.BOTH)

label = tk.Label(frame, text="Введите штрих-код:", font=font_style)
label.pack(pady=(0, 10))

entry = tk.Entry(frame, font=font_style, width=30)
entry.pack(pady=(0, 20))

button = tk.Button(frame, text="Сканировать", command=scan_barcode,
                  font=font_style, bg="#4CAF50", fg="white", height=1, width=15)
button.pack()

# Устанавливаем фокус на поле ввода
entry.focus_set()

# Привязываем нажатие Enter к кнопке сканирования
root.bind('<Return>', lambda event: scan_barcode())

root.mainloop()