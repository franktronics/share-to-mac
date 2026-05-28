from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QStatusBar,
)
from PyQt6.QtCore import Qt, QMetaObject, Q_ARG, pyqtSlot
from PyQt6.QtGui import QFont

from .frame_display import FrameDisplay
from ..network.udp_receiver import UDPReceiver
from ..utils.network_info import get_local_ip

DEFAULT_PORT = 5005


class MainWindow(QMainWindow):
    """
    Main application window.

    Displays incoming screen frames and allows the user to start/stop
    the UDP listener on a chosen port.
    """

    def __init__(self):
        super().__init__()
        self._receiver: UDPReceiver | None = None
        self._frame_count = 0

        self.setWindowTitle("ShareToMac")
        self.resize(800, 600)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(10)

        # Toolbar row
        toolbar = self._build_toolbar()
        root_layout.addLayout(toolbar)

        # Frame display
        self._display = FrameDisplay()
        root_layout.addWidget(self._display, stretch=1)

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._update_status("Waiting for connection…")

    def _build_toolbar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(12)

        # IP info label
        local_ip = get_local_ip()
        ip_label = QLabel(f"Your Mac IP:  <b>{local_ip}</b>")
        ip_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(ip_label)

        layout.addStretch()

        # Port selector
        port_label = QLabel("UDP Port:")
        layout.addWidget(port_label)

        self._port_spin = QSpinBox()
        self._port_spin.setRange(1024, 65535)
        self._port_spin.setValue(DEFAULT_PORT)
        self._port_spin.setFixedWidth(90)
        layout.addWidget(self._port_spin)

        # Start / Stop button
        self._toggle_btn = QPushButton("Start Listening")
        self._toggle_btn.setFixedWidth(140)
        font = QFont()
        font.setBold(True)
        self._toggle_btn.setFont(font)
        self._toggle_btn.clicked.connect(self._on_toggle)
        layout.addWidget(self._toggle_btn)

        return layout

    # ------------------------------------------------------------------
    # Slots

    @pyqtSlot()
    def _on_toggle(self) -> None:
        if self._receiver is None:
            self._start_receiver()
        else:
            self._stop_receiver()

    # ------------------------------------------------------------------
    # Receiver lifecycle

    def _start_receiver(self) -> None:
        port = self._port_spin.value()
        self._receiver = UDPReceiver(port=port, on_frame=self._on_frame_received)
        self._receiver.start()

        self._toggle_btn.setText("Stop Listening")
        self._port_spin.setEnabled(False)
        self._frame_count = 0
        self._update_status(f"Listening on port {port}…")

    def _stop_receiver(self) -> None:
        if self._receiver:
            self._receiver.stop()
            self._receiver = None

        self._toggle_btn.setText("Start Listening")
        self._port_spin.setEnabled(True)
        self._display.clear()
        self._display.setStyleSheet("background-color: #000000;")
        self._update_status("Stopped. Waiting for connection…")

    def closeEvent(self, event):
        self._stop_receiver()
        super().closeEvent(event)

    # ------------------------------------------------------------------
    # Frame callback (called from the receiver thread)

    def _on_frame_received(self, jpeg_data: bytes) -> None:
        self._frame_count += 1
        # Marshal back to the Qt main thread for UI update
        QMetaObject.invokeMethod(
            self,
            "_render_frame",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(bytes, jpeg_data),
        )

    @pyqtSlot(bytes)
    def _render_frame(self, jpeg_data: bytes) -> None:
        self._display.update_frame(jpeg_data)
        self._update_status(f"Receiving — frames: {self._frame_count}")

    # ------------------------------------------------------------------
    # Helpers

    def _update_status(self, message: str) -> None:
        self._status_bar.showMessage(message)
