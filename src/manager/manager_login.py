import sys
import requests
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QHBoxLayout,
)
from PySide6.QtCore import Qt

from manager_main_view import ManagerMainView

API_BASE_URL = "http://127.0.0.1:5000"


class ManagerLoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Manager Login")
        self.setMinimumSize(400, 500)

        self.main_view = None

        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Manager Login")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin-bottom: 16px;"
        )
        main_layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter manager username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        button_row = QHBoxLayout()
        button_row.setAlignment(Qt.AlignCenter)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)

        button_row.addWidget(self.login_button)

        buttons_widget = QWidget()
        buttons_widget.setLayout(button_row)
        main_layout.addWidget(buttons_widget)

        self.setCentralWidget(central)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter both Username and Password.",
            )
            return

        try:
            resp = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={"username": username, "password": password},
                timeout=5,
            )
        except requests.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Could not contact server:\n{e}")
            return

        if resp.status_code != 200:
            try:
                data = resp.json()
                error_msg = data.get("error", "Login failed.")
            except Exception:
                error_msg = f"Login failed ({resp.status_code})."
            QMessageBox.warning(self, "Error", error_msg)
            return

        data = resp.json()
        token = data.get("token")
        logged_in_username = data.get("username")
        role = data.get("role")

        if role is not None and role != "manager":
            QMessageBox.warning(
                self,
                "Access Denied",
                "This account is not a manager.",
            )
            return

        if not token or not logged_in_username:
            QMessageBox.warning(self, "Error", "Invalid login response from server.")
            return

        self.main_view = ManagerMainView(
            username=logged_in_username,
            token=token,
        )
        self.main_view.show()
        self.close()

def load_stylesheet(app: QApplication):
    base_dir = Path(__file__).resolve().parent
    style_path = base_dir / "resources" / "style.qss"

    try:
        with style_path.open("r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"style.qss not found at {style_path}, running without custom stylesheet")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_stylesheet(app)
    window = ManagerLoginWindow()
    window.show()
    sys.exit(app.exec())
