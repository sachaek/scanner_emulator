"""
Точка входа в приложение эмулятора сканера штрих-кодов
"""

import tkinter as tk
from emu.gui import ScannerGUI


def main():
    root = tk.Tk()
    app = ScannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()