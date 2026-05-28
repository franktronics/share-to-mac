from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage


class FrameDisplay(QLabel):
    """
    A QLabel subclass that accepts raw JPEG bytes and renders them
    scaled to fit the widget while preserving aspect ratio.
    """

    # Emitted when a frame is successfully decoded and rendered
    frame_rendered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(320, 180)
        self.setStyleSheet("background-color: #000000;")

    def update_frame(self, jpeg_data: bytes) -> None:
        """Decode JPEG bytes and render them into the label."""
        image = QImage.fromData(jpeg_data, "JPEG")
        if image.isNull():
            return

        pixmap = QPixmap.fromImage(image)
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)
        self.frame_rendered.emit()
