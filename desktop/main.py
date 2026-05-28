import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

from src.ui.main_window import MainWindow


def apply_dark_palette(app: QApplication) -> None:
    """Apply a system-consistent dark color palette."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(28, 28, 30))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(44, 44, 46))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(58, 58, 60))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(44, 44, 46))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(10, 132, 255))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("ShareToMac")
    app.setApplicationDisplayName("ShareToMac")
    apply_dark_palette(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
