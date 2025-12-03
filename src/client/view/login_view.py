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
    QHBoxLayout
)
from PySide6.QtCore import Qt
import sys


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Employee Login")
        self.setMinimumSize(400, 500)

        # ---- Central widget + main layout ----
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)

        # ---- Title label ----
        title_label = QLabel("Employee Login")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; margin-bottom: 16px;"
        )
        main_layout.addWidget(title_label)

        # ---- Form layout for Employee ID + Password ----
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)

        self.employee_id_input = QLineEdit()
        self.employee_id_input.setPlaceholderText("Enter your employee ID")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("Employee ID:", self.employee_id_input)
        form_layout.addRow("Password:", self.password_input)

        # Wrap form in a widget so we can center it
        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        # ---- Buttons row ----
        button_row = QHBoxLayout()
        button_row.setAlignment(Qt.AlignCenter)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)

        button_row.addWidget(self.login_button)
        
        buttons_widget = QWidget()
        buttons_widget.setLayout(button_row)
        main_layout.addWidget(buttons_widget)

        # Set central widget
        self.setCentralWidget(central_widget)

    def handle_login(self):
        employee_id = self.employee_id_input.text().strip()
        password = self.password_input.text().strip()

        if not employee_id or not password:
            QMessageBox.warning(self, "Missing Information", "Please enter both Employee ID and Password.")
            return

        # TODO: Replace this with real authentication (API/DB call)
        QMessageBox.information(
            self,
            "Login Clicked",
            f"Employee ID: {employee_id}\nPassword: {'*' * len(password)}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
