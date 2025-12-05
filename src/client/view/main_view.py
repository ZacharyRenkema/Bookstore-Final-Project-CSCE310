import sys
import requests
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
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import Qt

API_BASE_URL = "http://127.0.0.1:5000"


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
        self.setCentralWidget(central)


class MainView(QMainWindow):
    def __init__(self, username: str = "User", token: str = None):
        super().__init__()
        self.username = username
        self.token = token
        self.settings_window = None
        self.cart_items = []
        self.current_books = []
        self.setWindowTitle("Bookstore - Main View")
        self.setMinimumSize(1152, 648)
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(8)
        top_bar = QHBoxLayout()
        self.welcome_label = QLabel(f"Welcome Back {username}")
        self.welcome_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        top_bar.addWidget(self.welcome_label, alignment=Qt.AlignLeft)
        top_bar.addStretch()
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
        content_frame = QFrame()
        content_frame.setFrameShape(QFrame.Box)
        content_frame.setLineWidth(2)
        outer_layout = QHBoxLayout(content_frame)
        outer_layout.setContentsMargins(16, 16, 16, 16)
        outer_layout.setSpacing(16)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)
        search_controls_row = QHBoxLayout()
        search_controls_row.setSpacing(10)
        search_controls_row.addStretch()
        search_by_label = QLabel("Search by:")
        search_by_label.setStyleSheet("font-size: 14px;")
        self.search_by_combo = QComboBox()
        self.search_by_combo.addItems(["Title", "Author"])
        search_controls_row.addWidget(search_by_label)
        search_controls_row.addWidget(self.search_by_combo)
        search_controls_row.addStretch()
        left_layout.addLayout(search_controls_row)
        search_bar_row = QHBoxLayout()
        search_bar_row.setSpacing(10)
        search_bar_row.addStretch()
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
        self.search_button = QPushButton("Search")
        self.search_button.setMinimumHeight(40)
        self.search_button.clicked.connect(self.handle_search)
        search_bar_row.addWidget(self.search_input)
        search_bar_row.addWidget(self.search_button)
        search_bar_row.addStretch()
        left_layout.addLayout(search_bar_row)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(
            ["Title", "Author", "Buy Price", "Rent Price"]
        )
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setDefaultSectionSize(200)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        left_layout.addWidget(self.results_table)
        buy_rent_row = QHBoxLayout()
        buy_rent_row.setSpacing(10)
        buy_rent_row.addStretch()
        self.add_buy_button = QPushButton("Add Buy")
        self.add_buy_button.clicked.connect(self.handle_add_buy)
        self.add_rent_button = QPushButton("Add Rent")
        self.add_rent_button.clicked.connect(self.handle_add_rent)
        buy_rent_row.addWidget(self.add_buy_button)
        buy_rent_row.addWidget(self.add_rent_button)
        buy_rent_row.addStretch()
        left_layout.addLayout(buy_rent_row)
        outer_layout.addWidget(left_panel, stretch=3)
        cart_frame = QFrame()
        cart_frame.setFrameShape(QFrame.StyledPanel)
        cart_layout = QVBoxLayout(cart_frame)
        cart_layout.setContentsMargins(8, 8, 8, 8)
        cart_layout.setSpacing(8)
        cart_title = QLabel("Cart")
        cart_title.setAlignment(Qt.AlignCenter)
        cart_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        cart_layout.addWidget(cart_title)
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(3)
        self.cart_table.setHorizontalHeaderLabels(["Title", "Type", "Price"])
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        self.cart_table.horizontalHeader().setDefaultSectionSize(140)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cart_table.setSelectionMode(QTableWidget.SingleSelection)
        cart_layout.addWidget(self.cart_table)
        self.place_order_button = QPushButton("Place Order")
        self.place_order_button.clicked.connect(self.handle_place_order)
        cart_layout.addWidget(self.place_order_button)
        outer_layout.addWidget(cart_frame, stretch=1)
        root_layout.addWidget(content_frame)

    def set_logged_in_user(self, username: str):
        self.username = username
        self.welcome_label.setText(f"Welcome Back {username}")

    def handle_onclick_user(self):
        if self.settings_window is None:
            self.settings_window = UserSettingsWindow(self.username)
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def handle_search(self):
        keyword = self.search_input.text().strip()
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        params = {"q": keyword} if keyword else {}
        try:
            resp = requests.get(
                f"{API_BASE_URL}/books",
                headers=headers,
                params=params,
                timeout=5,
            )
        except requests.RequestException as e:
            QMessageBox.critical(
                self,
                "Network Error",
                f"Could not contact server:\n{e}",
            )
            return
        if resp.status_code != 200:
            try:
                data = resp.json()
                error_msg = data.get("error", f"Search failed ({resp.status_code}).")
            except Exception:
                error_msg = f"Search failed ({resp.status_code})."
            QMessageBox.warning(self, "Error", error_msg)
            return
        books = resp.json()
        self.populate_results_table(books)

    def populate_results_table(self, books):
        self.current_books = books
        self.results_table.setRowCount(len(books))
        for row, book in enumerate(books):
            title_item = QTableWidgetItem(str(book.get("title", "")))
            author_item = QTableWidgetItem(str(book.get("author", "")))
            buy_price = book.get("buy_price", 0)
            rent_price = book.get("rent_price", 0)
            buy_item = QTableWidgetItem(f"{buy_price:.2f}")
            rent_item = QTableWidgetItem(f"{rent_price:.2f}")
            self.results_table.setItem(row, 0, title_item)
            self.results_table.setItem(row, 1, author_item)
            self.results_table.setItem(row, 2, buy_item)
            self.results_table.setItem(row, 3, rent_item)

    def handle_add_buy(self):
        self.add_to_cart("buy")

    def handle_add_rent(self):
        self.add_to_cart("rent")

    def add_to_cart(self, kind: str):
        row = self.results_table.currentRow()
        if row < 0 or row >= len(self.current_books):
            QMessageBox.warning(self, "No Selection", "Please select a book first.")
            return
        book = self.current_books[row]
        book_id = book.get("id")
        title = book.get("title", "")
        if kind == "buy":
            price = float(book.get("buy_price", 0))
        else:
            price = float(book.get("rent_price", 0))
        item = {
            "book_id": book_id,
            "title": title,
            "kind": kind,
            "price": price,
        }
        self.cart_items.append(item)
        self.refresh_cart_table()
        self.update_cart_label()

    def refresh_cart_table(self):
        self.cart_table.setRowCount(len(self.cart_items))
        for row, item in enumerate(self.cart_items):
            title_item = QTableWidgetItem(str(item.get("title", "")))
            kind_item = QTableWidgetItem(str(item.get("kind", "")))
            price_item = QTableWidgetItem(f"{item.get('price', 0):.2f}")
            self.cart_table.setItem(row, 0, title_item)
            self.cart_table.setItem(row, 1, kind_item)
            self.cart_table.setItem(row, 2, price_item)

    def update_cart_label(self):
        self.cart_label.setText(f"Cart: {len(self.cart_items)}")

    def handle_place_order(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Your cart is empty.")
            return
        if not self.token:
            QMessageBox.warning(self, "Not Authenticated", "You must be logged in to place an order.")
            return
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        items_payload = []
        for item in self.cart_items:
            items_payload.append(
                {
                    "book_id": item["book_id"],
                    "kind": item["kind"],
                    "quantity": 1,
                }
            )
        try:
            resp = requests.post(
                f"{API_BASE_URL}/orders",
                headers=headers,
                json={"items": items_payload},
                timeout=5,
            )
        except requests.RequestException as e:
            QMessageBox.critical(
                self,
                "Network Error",
                f"Could not contact server:\n{e}",
            )
            return
        if resp.status_code != 201:
            try:
                data = resp.json()
                error_msg = data.get("error", f"Order failed ({resp.status_code}).")
            except Exception:
                error_msg = f"Order failed ({resp.status_code})."
            QMessageBox.warning(self, "Error", error_msg)
            return
        data = resp.json()
        order_id = data.get("id")
        total_amount = data.get("total_amount")
        QMessageBox.information(
            self,
            "Order Placed",
            f"Order #{order_id} placed successfully.\nTotal: {total_amount:.2f}",
        )
        self.cart_items = []
        self.refresh_cart_table()
        self.update_cart_label()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainView(username="Alice", token=None)
    window.show()
    sys.exit(app.exec())
