"""
Точка входа в приложение эмулятора сканера штрих-кодов (PyQt)
"""

import sys
from PyQt5.QtWidgets import QApplication
from emu.gui import ScannerGUI


def main():
    app = QApplication(sys.argv)
    window = ScannerGUI()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())