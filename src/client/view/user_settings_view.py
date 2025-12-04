from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel
)
from PySide6.QtCore import Qt

class UserSettingsWindow(QMainWindow):
    def __init__(self, username: str):
        super().__init__()

        self.setWindowTitle("User Settings")
        self.setMinimumSize(1200, 1000)

        central = QWidget()
        layout = QVBoxLayout(central)

        title = QLabel(f"Settings for {username}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        layout.addWidget(title)

        # TODO: add real settings controls here

        self.setCentralWidget(central)