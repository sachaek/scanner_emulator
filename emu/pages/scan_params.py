"""
Диалог параметров сканирования: просмотр/редактирование конфигурации с применением и сбросом.
"""

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFormLayout, QDialogButtonBox, QDoubleSpinBox, QSpinBox
from PyQt5.QtCore import Qt
from ..config import get_scanner_config, save_scanner_override, reset_scanner_override
from ..theme import ThemedDialog


class ScanParamsDialog(ThemedDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Параметры сканирования")
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        subtitle = QLabel("Настройте параметры и нажмите Применить")
        subtitle.setAlignment(Qt.AlignLeft)
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)

        cfg = get_scanner_config()

        self.sp_initial = QDoubleSpinBox()
        self.sp_initial.setRange(0.0, 10.0)
        self.sp_initial.setSingleStep(0.05)
        self.sp_initial.setDecimals(3)
        self.sp_initial.setValue(float(cfg.get('initial_delay', 2.0)))

        self.sp_first = QDoubleSpinBox()
        self.sp_first.setRange(0.0, 1.0)
        self.sp_first.setSingleStep(0.005)
        self.sp_first.setDecimals(3)
        self.sp_first.setValue(float(cfg.get('first_char_delay', 0.05)))

        self.sp_char = QDoubleSpinBox()
        self.sp_char.setRange(0.0, 1.0)
        self.sp_char.setSingleStep(0.005)
        self.sp_char.setDecimals(3)
        self.sp_char.setValue(float(cfg.get('char_delay', 0.02)))

        self.sp_hold = QDoubleSpinBox()
        self.sp_hold.setRange(0.0, 1.0)
        self.sp_hold.setSingleStep(0.001)
        self.sp_hold.setDecimals(3)
        self.sp_hold.setValue(float(cfg.get('key_hold_delay', 0.005)))

        self.sp_maxlen = QSpinBox()
        self.sp_maxlen.setRange(1, 256)
        self.sp_maxlen.setSingleStep(1)
        self.sp_maxlen.setValue(int(cfg.get('max_length', 30)))

        form.addRow("Задержка перед сканированием (сек):", self.sp_initial)
        form.addRow("Задержка первого символа (сек):", self.sp_first)
        form.addRow("Задержка между символами (сек):", self.sp_char)
        form.addRow("Удержание клавиши (сек):", self.sp_hold)
        form.addRow("Макс. длина штрих-кода:", self.sp_maxlen)

        layout.addLayout(form)

        buttons = QDialogButtonBox()
        btn_apply = buttons.addButton("Применить", QDialogButtonBox.AcceptRole)
        btn_reset = buttons.addButton("Восстановить по умолчанию", QDialogButtonBox.ResetRole)
        btn_close = buttons.addButton("Закрыть", QDialogButtonBox.RejectRole)

        btn_apply.clicked.connect(self.on_apply)
        btn_reset.clicked.connect(self.on_reset)
        btn_close.clicked.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def _collect_values(self):
        return {
            'initial_delay': float(self.sp_initial.value()),
            'first_char_delay': float(self.sp_first.value()),
            'char_delay': float(self.sp_char.value()),
            'key_hold_delay': float(self.sp_hold.value()),
            'max_length': int(self.sp_maxlen.value()),
        }

    def on_apply(self):
        save_scanner_override(self._collect_values())
        self.accept()

    def on_reset(self):
        reset_scanner_override()
        # Обновляем значения на форме с умолчаниями
        cfg = get_scanner_config()
        self.sp_initial.setValue(float(cfg.get('initial_delay', 2.0)))
        self.sp_first.setValue(float(cfg.get('first_char_delay', 0.05)))
        self.sp_char.setValue(float(cfg.get('char_delay', 0.02)))
        self.sp_hold.setValue(float(cfg.get('key_hold_delay', 0.005)))
        self.sp_maxlen.setValue(int(cfg.get('max_length', 30)))


