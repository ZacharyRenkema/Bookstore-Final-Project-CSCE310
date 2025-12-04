import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt


class UserSettingsWindow(QMainWindow):
    def __init__(self, username: str):
        super().__init__()
        self.setWindowTitle("User Settings")
        self.setMinimumSize(600, 400)

        central = QWidget()
        layout = QVBoxLayout(central)

        title = QLabel(f"Settings for {username}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        layout.addWidget(title)
        # TODO: add real settings widgets here

        self.setCentralWidget(central)


class MainView(QMainWindow):
    def __init__(self, username: str = "User"):
        super().__init__()

        self.username = username
        self.settings_window = None  # keep a reference

        self.setWindowTitle("Bookstore - Main View")
        self.setMinimumSize(1152, 648)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(8)

        # ========== TOP BAR ==========
        top_bar = QHBoxLayout()

        # Left: Welcome label
        self.welcome_label = QLabel(f"Welcome Back {username}")
        self.welcome_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        top_bar.addWidget(self.welcome_label, alignment=Qt.AlignLeft)

        top_bar.addStretch()  # pushes the right widgets to the far right

        # Right: User settings + Cart
        self.user_settings_button = QPushButton("User Settings")
        self.user_settings_button.setFlat(True)
        self.user_settings_button.setStyleSheet("font-size: 12px;")
        self.user_settings_button.clicked.connect(self.handle_onclick_user)

        self.cart_label = QLabel("Cart: 0")
        self.cart_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        top_bar.addWidget(self.user_settings_button, alignment=Qt.AlignRight)
        top_bar.addSpacing(16)
        top_bar.addWidget(self.cart_label, alignment=Qt.AlignRight)

        root_layout.addLayout(top_bar)

        # ========== INNER CONTENT FRAME (big rectangle) ==========
        content_frame = QFrame()
        content_frame.setFrameShape(QFrame.Box)
        content_frame.setLineWidth(2)
        content_frame_layout = QVBoxLayout(content_frame)
        content_frame_layout.setContentsMargins(40, 40, 40, 40)
        content_frame_layout.setSpacing(30)

        # Center everything inside the frame vertically
        content_frame_layout.addStretch()

        # ---- Search controls row (Search by: [dropdown]) ----
        search_controls_row = QHBoxLayout()
        search_controls_row.setSpacing(10)
        search_controls_row.addStretch()

        search_by_label = QLabel("Search by:")
        search_by_label.setStyleSheet("font-size: 14px;")

        self.search_by_combo = QComboBox()
        self.search_by_combo.addItems(["Title", "Author", "ISBN", "Category"])

        search_controls_row.addWidget(search_by_label)
        search_controls_row.addWidget(self.search_by_combo)
        search_controls_row.addStretch()

        content_frame_layout.addLayout(search_controls_row)

        # ---- Search bar (pill-shaped QLineEdit) ----
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for books...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.search_input.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid black;
                border-radius: 20px;
                padding-left: 16px;
                padding-right: 16px;
                font-size: 14px;
            }
            """
        )

        # center the search bar horizontally
        search_bar_row = QHBoxLayout()
        search_bar_row.addStretch()
        search_bar_row.addWidget(self.search_input)
        search_bar_row.addStretch()

        content_frame_layout.addLayout(search_bar_row)

        content_frame_layout.addStretch()

        root_layout.addWidget(content_frame)

    def set_logged_in_user(self, username: str):
        self.username = username
        self.welcome_label.setText(f"Welcome Back {username}")

    def handle_onclick_user(self):
        # Open (or focus) the user settings window
        if self.settings_window is None:
            self.settings_window = UserSettingsWindow(self.username)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainView(username="Alice")
    window.show()
    sys.exit(app.exec())
