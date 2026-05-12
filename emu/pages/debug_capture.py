"""Диалог захвата HID сканнера: запуск/останов, просмотр захватов, лог."""

from __future__ import annotations

import os

from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QCheckBox,
    QTextEdit,
    QVBoxLayout,
)

from ..paths import get_user_data_dir
from ..scanner_capture import ScannerCapture, ScanCapture
from ..theme import ThemedDialog


class _CaptureSignalBridge(QObject):
    """QObject с сигналом для thread-safe передачи захватов из потока pynput в GUI."""
    captured = pyqtSignal(object)


class DebugCaptureDialog(ThemedDialog):
    """Диалог режима отладки: захват и анализ ввода HID сканера."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bridge = _CaptureSignalBridge()
        self._bridge.captured.connect(self._on_capture_gui)

        self._capture = ScannerCapture(on_capture=self._on_capture_thread)
        self._capture_index = 0

        self.setWindowTitle("Захват сканнера")
        self.setModal(False)
        self.resize(640, 480)
        self._setup_ui()

    # --- UI setup ---

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # --- Панель управления ---
        ctrl = QHBoxLayout()

        self._btn_toggle = QPushButton("Начать захват")
        self._btn_toggle.clicked.connect(self._on_toggle)
        ctrl.addWidget(self._btn_toggle)

        self._cb_suppress = QCheckBox("Блокировать ввод")
        self._cb_suppress.setToolTip(
            "Перехватывать нажатия, не пропуская их в другие окна"
        )
        ctrl.addWidget(self._cb_suppress)

        self._status_label = QLabel("Остановлен")
        self._status_label.setStyleSheet("color: #999; font-weight: bold;")
        ctrl.addWidget(self._status_label)

        ctrl.addStretch()
        layout.addLayout(ctrl)

        # --- Список захватов + детали ---
        split = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_label = QLabel("Захваты:")
        left_layout.addWidget(left_label)

        self._list_widget = QListWidget()
        self._list_widget.currentRowChanged.connect(self._on_selection_changed)
        self._list_widget.setMinimumWidth(200)
        left_layout.addWidget(self._list_widget)

        left_widget_container = QHBoxLayout()
        left_widget_container.addLayout(left_layout)
        split.addLayout(left_widget_container, 1)

        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_label = QLabel("Детали:")
        right_layout.addWidget(right_label)

        self._detail_text = QTextEdit()
        self._detail_text.setReadOnly(True)
        mono = QFont("Consolas", 9)
        mono.setStyleHint(QFont.Monospace)
        self._detail_text.setFont(mono)
        right_layout.addWidget(self._detail_text)

        split.addLayout(right_layout, 2)

        layout.addLayout(split, 1)

        # --- Информация о логах ---
        log_dir = os.path.join(get_user_data_dir(), "debug_logs")
        self._log_label = QLabel(
            f"Лог: {log_dir}"
        )
        self._log_label.setWordWrap(True)
        self._log_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(self._log_label)

        self.setLayout(layout)

    # --- Обработчики ---

    def _on_toggle(self):
        if self._capture.is_running:
            self._capture.stop()
            self._btn_toggle.setText("Начать захват")
            self._cb_suppress.setEnabled(True)
            self._status_label.setText("Остановлен")
            self._status_label.setStyleSheet("color: #999; font-weight: bold;")
        else:
            suppress = self._cb_suppress.isChecked()
            self._capture.start(suppress=suppress)
            self._btn_toggle.setText("Остановить захват")
            self._cb_suppress.setEnabled(False)
            self._status_label.setText("Активен")
            self._status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

    def _on_capture_thread(self, capture: ScanCapture):
        """Вызывается из потока pynput — пробрасываем в GUI через сигнал."""
        self._bridge.captured.emit(capture)

    def _on_capture_gui(self, capture: ScanCapture):
        """Вызывается в GUI-потоке — обновляем UI."""
        self._capture_index += 1
        idx = self._capture_index

        # Показываем первые 20 символов barcode + таймстемп
        barcode_preview = capture.barcode[:20]
        if len(capture.barcode) > 20:
            barcode_preview += "…"
        item_text = f"{idx}: {barcode_preview}  ({capture.total_duration_ms}ms)"

        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, idx)  # храним индекс для поиска
        self._list_widget.addItem(item)
        self._list_widget.setCurrentItem(item)

        # Обновляем счётчик логов
        self._log_label.setText(
            f"Лог: {os.path.join(get_user_data_dir(), 'debug_logs')}  |  "
            f"Захватов: {self._capture_index}"
        )

    def _on_selection_changed(self, row: int):
        """Показать детали выбранного захвата."""
        if row < 0 or row >= len(self._capture.captures):
            self._detail_text.clear()
            return
        capture = self._capture.captures[row]
        self._detail_text.setPlainText(
            self._capture.format_capture_detail(capture)
        )

    def closeEvent(self, event):
        """При закрытии диалога останавливаем захват, если активен."""
        self._capture.stop()
        super().closeEvent(event)
