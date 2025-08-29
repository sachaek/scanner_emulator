"""
Точка входа в приложение эмулятора сканера штрих-кодов (PyQt)
"""

import sys
from PyQt5.QtWidgets import QApplication
from emu.gui import ScannerGUI
from emu.theme import apply_theme


def main():
    app = QApplication(sys.argv)

    # Единая тема оформления
    apply_theme(app)

    window = ScannerGUI()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())