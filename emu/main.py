"""
Точка входа в приложение эмулятора сканера штрих-кодов (PyQt)
"""

import sys
from PyQt5.QtWidgets import QApplication
from emu.gui import ScannerGUI


def main():
    app = QApplication(sys.argv)

    # Единый тёмный стиль (QSS) по всему приложению
    app.setStyle('Fusion')
    qss = """
    QWidget {
        background-color: #121212;
        color: #E0E0E0;
    }
    QLabel { color: #E0E0E0; }
    QLineEdit {
        background: #1E1E1E;
        color: #E0E0E0;
        border: 1px solid #333333;
        border-radius: 6px;
        padding: 6px 8px;
        selection-background-color: #2F6FED;
        selection-color: #FFFFFF;
    }
    QLineEdit:focus { border: 1px solid #4F8CFF; }

    QPushButton {
        background: #2A2A2A;
        color: #E0E0E0;
        border: 1px solid #3A3A3A;
        border-radius: 6px; /* чуть меньше скругление */
        padding: 6px 12px;
    }
    QPushButton:hover { background: #323232; }
    QPushButton:pressed { background: #262626; }
    QPushButton:disabled {
        color: #777777;
        background: #1C1C1C;
        border-color: #2A2A2A;
    }

    QMessageBox { background-color: #1A1A1A; }

    QMenuBar {
        background-color: #171717;
        color: #E0E0E0;
        border-bottom: 1px solid #2A2A2A;
    }
    QMenuBar::item {
        background: transparent;
        padding: 4px 8px;
        margin: 0 2px;
        border-radius: 4px;
    }
    QMenuBar::item:selected { background: #2A2A2A; }

    QMenu {
        background-color: #1B1B1B;
        color: #E0E0E0;
        border: 1px solid #2A2A2A;
    }
    QMenu::item { padding: 6px 18px; }
    QMenu::item:selected { background-color: #2F2F2F; }
    """
    app.setStyleSheet(qss)

    window = ScannerGUI()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())