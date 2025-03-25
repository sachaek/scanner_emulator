from pynput.keyboard import Controller, Key
import tkinter as tk
import time


def scan_barcode():
    barcode = entry.get()
    if len(barcode) > 30:
        label.config(text="Длина строки не может быть больше 30")
        return

    root.withdraw()  # Скрываем окно
    time.sleep(0.5)  # Даём время свернуть GUI

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


root = tk.Tk()
root.title("Эмулятор сканера")

label = tk.Label(root, text="Введите штрих-код:")
label.pack()

entry = tk.Entry(root)
entry.pack()

button = tk.Button(root, text="Сканировать", command=scan_barcode)
button.pack()

root.mainloop()