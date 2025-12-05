import sys
import requests
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
    QComboBox,
)
from PySide6.QtCore import Qt

from main_view import MainView

API_BASE_URL = "http://127.0.0.1:5000"


class RegistrationWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create Account")
        self.setMinimumSize(450, 550)

        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Create New Account")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 22px; font-weight: bold; margin-bottom: 16px;"
        )
        main_layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter a valid email address")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Choose a password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Re-type your password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["customer", "manager"])

        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Confirm Password:", self.confirm_password_input)
        form_layout.addRow("Role:", self.role_combo)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        button_row = QHBoxLayout()
        button_row.setAlignment(Qt.AlignCenter)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.handle_register)

        button_row.addWidget(self.register_button)

        buttons_widget = QWidget()
        buttons_widget.setLayout(button_row)
        main_layout.addWidget(buttons_widget)

        self.setCentralWidget(central)

    def handle_register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        role = self.role_combo.currentText()

        if not username or not email or not password or not confirm_password:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please fill in all fields.",
            )
            return

        if password != confirm_password:
            QMessageBox.warning(
                self,
                "Password Mismatch",
                "Password and confirmation do not match.",
            )
            return

        try:
            resp = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "role": role,
                },
                timeout=5,
            )
        except requests.RequestException as e:
            QMessageBox.critical(
                self,
                "Network Error",
                f"Could not contact server:\n{e}",
            )
            return

        if resp.status_code == 201:
            QMessageBox.information(
                self,
                "Success",
                "Registration successful. You can now log in.",
            )
            self.close()
        else:
            try:
                data = resp.json()
                error_msg = data.get("error", "Registration failed.")
            except Exception:
                error_msg = f"Registration failed ({resp.status_code})."
            QMessageBox.warning(self, "Error", error_msg)


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Employee Login")
        self.setMinimumSize(400, 500)

        self.auth_token = None
        self.logged_in_username = None
        self.logged_in_role = None
        self.main_view = None
        self.register_window = None

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Employee Login")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin-bottom: 16px;"
        )
        main_layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
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

        self.create_account_button = QPushButton("Create Account")
        self.create_account_button.clicked.connect(self.open_registration)

        button_row.addWidget(self.login_button)
        button_row.addWidget(self.create_account_button)

        buttons_widget = QWidget()
        buttons_widget.setLayout(button_row)
        main_layout.addWidget(buttons_widget)

        self.setCentralWidget(central_widget)

    def open_registration(self):
        if self.register_window is None:
            self.register_window = RegistrationWindow(self)
        self.register_window.show()
        self.register_window.raise_()
        self.register_window.activateWindow()

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
            QMessageBox.critical(
                self,
                "Network Error",
                f"Could not contact server:\n{e}",
            )
            return

        if resp.status_code == 200:
            data = resp.json()
            token = data.get("token")
            logged_in_username = data.get("username")

            # print("DEBUG TOKEN FROM LOGIN:", token)  # optional debug

            self.main_view = MainView(
                username=logged_in_username,
                token=token,
            )
            self.main_view.show()
            self.close()
        else:
            try:
                data = resp.json()
                error_msg = data.get("error", "Login failed.")
            except Exception:
                error_msg = f"Login failed ({resp.status_code})."
            QMessageBox.warning(self, "Error", error_msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
